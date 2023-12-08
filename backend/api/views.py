import json
import os
from datetime import timedelta

from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views import View
from products.models import (Dealer, DealerPrice, Product, ProductDealerKey,
                             Statistics)
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from tools.import_csv import (export_model_to_csv_binary,
                              import_dealers_from_csv, import_prices_from_csv,
                              import_products_from_csv, save_json)

from ML.main_script import result

from .forms import MarkupRequestForm
from .serializers import (DealerPriceSerializer, DealerSerializer,
                          ProductDealerKeySerializer, ProductSerializer,
                          StatisticsSerializer)

NUMBERS_OF_FILES = 3
AMOUNT_RESULT = 10
DEALER_FILE = 'marketing_dealer.csv'
PRODUCT_FILE = 'marketing_product.csv'
PRICES_FILE = 'marketing_dealerprice.csv'


class DealerListCreateView(viewsets.ModelViewSet):
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer
    

class ProductListCreateView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class DealerPriceListCreateView(viewsets.ModelViewSet):
    queryset = DealerPrice.objects.all()
    serializer_class = DealerPriceSerializer


class ProductDealerKeyListCreateView(viewsets.ModelViewSet):
    queryset = ProductDealerKey.objects.all()
    serializer_class = ProductDealerKeySerializer


class LoadDataView(APIView):
    """
    Представление для загрузки данных.
    В теле запроса приходят три файла:
    - marketing_dealer.csv
    - marketing_product.csv
    - marketing_dealerprice.csv
    Класс сохраняет файлы локально в директорию 'data/temp_data/',
    После вызывает функцию загрузки данных в БД.
    """
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        files = request.data.getlist('file')

        # Проверка, что переданы три файла csv
        if len(files) != NUMBERS_OF_FILES:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Сохранение файлов локально
        save_path = 'data/temp_data/'
        for file in files:
            with open(os.path.join(save_path, file.name), 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        # Импорт файлов в базу данных
        try:
            import_dealers_from_csv(os.path.join(save_path, DEALER_FILE))
            import_products_from_csv(os.path.join(save_path, PRODUCT_FILE))
            import_prices_from_csv(os.path.join(save_path, PRICES_FILE))
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # После импорта файлы удаляются
        os.remove(os.path.join(save_path, DEALER_FILE))
        os.remove(os.path.join(save_path, PRODUCT_FILE))
        os.remove(os.path.join(save_path, PRICES_FILE))

        # Экспорт очищенных файлов из базы данных в CSV
        # и загрузка в предобученную модель
        products_file = export_model_to_csv_binary(Product)
        prices_file = export_model_to_csv_binary(DealerPrice)
        ds_result = result(products_file,
                           prices_file,
                           AMOUNT_RESULT)

        # Сохранение результата работы модели и создание записей в базе данных
        json_file_path = 'data/temp_data/matching_prices.json'
        save_json(json_data=ds_result,
                  file_name=json_file_path)
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        dict_data = list(data.items())
        os.remove(json_file_path)
        prices_urls = {
            price.product_url: price for price in DealerPrice.objects.all()
        }
        products_articles = {product.article: product for product in Product.objects.all()}
        matching_data = []
        for price in dict_data:
            for count, product in enumerate(price[1]):
                matching_data.append(
                    ProductDealerKey(
                        key=prices_urls[price[0]],
                        product_id=products_articles[product],
                        compliance_number=count
                    )
                )
        ProductDealerKey.objects.bulk_create(matching_data)
        return Response(status=status.HTTP_201_CREATED)
    
    def get(self, request, *args, **kwargs):
        # обработка GET запроса
        return Response(status=status.HTTP_200_OK)


class MainView(View):
    """
    Представление для отображения списка товаров с возможностью фильтрации.

    GET-запрос:
    - Параметры запроса:
      - start_date: Начальная дата фильтрации (необязательно, формат: 'YYYY-MM-DD').
      - end_date: Конечная дата фильтрации (необязательно, формат: 'YYYY-MM-DD').
      - status: Фильтр по статусу ('matched' или 'unmatched', необязательно).
      - dealers: Список идентификаторов продавцов для дополнительной фильтрации (необязательно).
      - num_matches: Количество вариантов соответствия, которое нужно предоставить (необязательно).

    POST-запрос:
    - Параметры запроса:
      - action: Действие ('Да', 'Нет' или 'Сопоставить').
      - product_id: Идентификатор товара.
    
    Возвращает JsonResponse со списком товаров, в том числе удовлетворяющих заданным критериям фильтрации,
    а также предоставляет количество совпадений в соответствии с параметром num_matches.
    """

    def get(self, request, *args, **kwargs):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status_filter = request.GET.get('status')
        dealer_ids = request.GET.getlist('dealers[]')
        num_matches = request.GET.get('num_matches')

        # Логика для определения начальной и конечной даты, если не заданы
        if not start_date or not end_date:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=6)

        if not isinstance(start_date, timezone.datetime):
            """
            Если начальная дата не является экземпляром datetime, преобразует её из строки в объект datetime.

            Параметры:
            - start_date (str или datetime): Начальная дата фильтрации.

            Результат:
            - start_date преобразуется в объект datetime, если она не является таковым.
            """
            start_date = parse_date(start_date)

        if not isinstance(end_date, timezone.datetime):
            """
            Если конечная дата не является экземпляром datetime, преобразует её из строки в объект datetime.

            Параметры:
            - end_date (str или datetime): Конечная дата фильтрации.

            Результат:
            - end_date преобразуется в объект datetime, если она не является таковым.
            """
            end_date = parse_date(end_date)

        # Дополнительная фильтрация по dealer_ids
        if dealer_ids:
            dealer_filter = {'dealer__id__in': dealer_ids}
        else:
            dealer_filter = {}

        if status_filter:
            """
            Если параметр status_filter задан, устанавливает фильтр по статусу товаров.

            Параметры:
            - status_filter (str): Фильтр по статусу ('matched' или 'unmatched').

            Действия:
            - Если status_filter равен 'matched', фильтрует товары, у которых имеются соответствия.
            - Если status_filter равен 'unmatched', фильтрует товары, у которых нет соответствий.

            Результат:
            - dealer_filter обновляется в соответствии с заданным статусом для последующего использования
            в фильтрации товаров.
            """
            
            if status_filter == 'matched':
                dealer_filter['product_dealer_keys__isnull'] = False
            elif status_filter == 'unmatched':
                dealer_filter['product_dealer_keys__isnull'] = True

        # Получение списка товаров из базы данных
        products_info_objects = Product.objects.filter(**dealer_filter)

        # Сериализация данных о товарах
        products_info_serialized = ProductSerializer(products_info_objects, many=True).data

        # Получение списка вариантов соответствия для каждого товара
        matching_options = []
        for product in products_info_objects:
            product_key = product.id
            matching_options_url = reverse('matching_options', args=[product_key])
            matching_options.append(matching_options_url)

        # Логика для num_matches
        if num_matches:
            # Ограничение количества вариантов соответствия в соответствии с параметром num_matches
            num_matches = int(num_matches)
            matching_options = matching_options[:num_matches]

        # Сериализация цен продавцов
        dealer_prices = DealerPrice.objects.filter(**dealer_filter)
        dealer_prices_serialized = DealerPriceSerializer(dealer_prices, many=True).data

        # Сериализация данных о продавцах
        dealers = Dealer.objects.filter(**dealer_filter)
        dealers_serialized = DealerSerializer(dealers, many=True).data

        return JsonResponse({
            'products': products_info_serialized,
            'matching_options': matching_options,
            'dealer_prices': dealer_prices_serialized,
            'dealers': dealers_serialized,
        })
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        
        if action == 'Да':
            # Обработка "Да"
            # Добавить логику для "Да"
            return JsonResponse({"message": "Да"})
        elif action == 'Нет':
            # Обработка "Нет"
            # Добавить логику для "Нет"
            return JsonResponse({"message": "Нет"})
        elif action == 'Сопоставить':
            # Обработка "Сопоставить"
            # Добавить логику для "Сопоставить"
            return JsonResponse({"message": "Сопоставить"})
        else:
            return JsonResponse({"error": "Неверное действие"}, status=400) # На случай возможных изменений в коде
    

class MatchingOptionsView(View):
    """
    Представление для получения вариантов соответствия товара.
    """

    def get(self, request, product_id, *args, **kwargs):
        """
        Обработчик GET-запроса для получения вариантов соответствия товара.

        Возвращает JsonResponse с вариантами соответствия.
        """
        product_dealer_keys = ProductDealerKey.objects.filter(product_id=product_id)

        # Сериализация объектов с использованием ProductDealerKeySerializer
        serializer = ProductDealerKeySerializer(product_dealer_keys, many=True)
        serialized_data = serializer.data

        return JsonResponse({"matching_options": serialized_data})
            
    
class MarkupProductView(View):
    
    def get(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        product_dealer_key = product.product_dealer_keys.first()

        if product_dealer_key:
            return JsonResponse({
                "product_id": product_id,
                "marked": True,
                "markup_id": product_dealer_key.id,
                "key": product_dealer_key.key,
                "order": product_dealer_key.order,
            })
        else:
            return JsonResponse({"product_id": product_id, "marked": False})

    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        markup_request_form = MarkupRequestForm(request.POST)

        if markup_request_form.is_valid():
            key = markup_request_form.cleaned_data['key']
            markup_count = ProductDealerKey.objects.filter(product=product).count()

            # Увеличиваем счетчик для новой разметки
            product_dealer_key = ProductDealerKey.objects.create(key=key, product=product, order=markup_count + 1)

            return JsonResponse({
                "message": f"Разметка товара {product_id} завершена",
                "markup_id": product_dealer_key.id,
            })
        else:
            return JsonResponse({"error": r"Неверные данные формы"}, status=400)     


class StatisticsView(View):
    """
    Представление для работы со статистикой.
    """
    
    def get(self, request):
        # Получаем начальную и конечную дату из запроса
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Используем даты из запроса или значения по умолчанию
        if not start_date_str or not end_date_str:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)

        # Статистика общего количества размеченных товаров за выбранный период
        total_markup_count = ProductDealerKey.objects.filter(
            marking_date__range=[start_date, end_date]
        ).count()

        # Статистика выбора предложенных вариантов за выбранный период
        chosen_options_stats = ProductDealerKey.objects.filter(
            marking_date__range=[start_date, end_date]
        ).exclude(key=None).values(
            'product_id', 'dealer_id', 'product_id__category_id'
        ).annotate(
            total_choices=Count('id'),
            chosen_option_count=Count('key')
        )

        # Статистика по порядку выбора вариантов за выбранный период
        choices_order = chosen_options_stats.values(
            'choices_order', 'product_id', 'dealer_id', 'product_id__category_id'
        ).annotate(
            choices_count=Count('choices_order')
        ).order_by('choices_order')

        # Счетчик для порядкового номера выбора вариантов
        choices_counter = 1

        # Присвоение порядкового номера выбора вариантов
        for stat in choices_order:
            stat['choices_order'] = choices_counter
            choices_counter += 1

        # Преобразование QuerySet в список для сохранения в модель
        chosen_options_stats_list = list(chosen_options_stats)
        choices_order_list = list(choices_order)

        # Статистика по тому, как часто ни один вариант не выбран
        none_chosen_count = chosen_options_stats.filter(chosen_option_count=0).count()

        # Получаем дилеров и категории
        dealers = Dealer.objects.all()
        categories = Product.objects.values('category_id').distinct()

        # Сериализация статистики
        statistics_data = Statistics.objects.all()
        statistics_serialized = StatisticsSerializer(statistics_data, many=True).data

        context = {
            'statistics': statistics_serialized,
            'start_date': start_date.strftime("%Y-%m-%d"),
            'end_date': end_date.strftime("%Y-%m-%d"),
            'total_markup_count': total_markup_count,
            'chosen_options_stats': chosen_options_stats_list,
            'choices_order': choices_order_list,
            'none_chosen_count': none_chosen_count,
            'dealers': dealers,
            'categories': categories,
        }

        # Сохранение статистики в базе данных
        Statistics.objects.create(
            start_date=start_date,
            end_date=end_date,
            total_markup_count=total_markup_count,
            none_chosen_count=none_chosen_count,
            choices_order=choices_order_list,
            chosen_options_stats=chosen_options_stats_list,
        )

        return JsonResponse(context)


class VariantStatisticsView(View):
    """
    Представление для статистики по номеру варианта.
    """

    def get(self, request):
        # Логика для получения статистики по порядковому номеру выбора и невыбранным вариантам
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Ваша логика для фильтрации ProductDealerKey и сбора статистики
        # Пример:
        chosen_options_stats = ProductDealerKey.objects.filter(
            marking_date__range=[start_date, end_date]
        ).values(
            'choices_order', 'product_id', 'dealer_id', 'product_id__category_id'
        ).annotate(
            choices_count=Count('choices_order'),
            chosen_option_count=Count('id', filter=~Q(key=None)),
        ).order_by('choices_order')

        # Счетчик для порядкового номера выбора вариантов
        choices_counter = 1

        # Присвоение порядкового номера выбора вариантов
        for stat in chosen_options_stats:
            stat['choices_order'] = choices_counter
            choices_counter += 1

        # Преобразование QuerySet в список для сохранения в модель
        chosen_options_stats_list = list(chosen_options_stats)

        # Статистика по тому, как часто ни один вариант не выбран за выбранный период
        none_chosen_count = chosen_options_stats.filter(chosen_option_count=0).count()

        # Получаем дилеров и категории
        dealers = Dealer.objects.all()
        categories = Product.objects.values('category_id').distinct()

        # Сериализация статистики
        statistics_data = Statistics.objects.all()
        statistics_serialized = StatisticsSerializer(statistics_data, many=True).data

        context = {
            'statistics': statistics_serialized,
            'start_date': start_date.strftime("%Y-%m-%d") if start_date else None,
            'end_date': end_date.strftime("%Y-%m-%d") if end_date else None,
            'chosen_options_stats': chosen_options_stats_list,
            'none_chosen_count': none_chosen_count,
            'dealers': dealers,
            'categories': categories,
        }

        return JsonResponse(context)
