from datetime import timedelta
from django.shortcuts import render
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views import View
from products.models import (Dealer, DealerPrice, Product, ProductDealerKey,
                             Statistics)
from rest_framework import viewsets

from .forms import MarkupRequestForm
from .serializers import (DealerPriceSerializer, DealerSerializer,
                          ProductDealerKeySerializer, ProductSerializer,
                          StatisticsSerializer)


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


class LoadDataView(View):
    """
    Представление для загрузки данных.
    """

    def post(self, request, *args, **kwargs):
        """
        Обработчик POST-запроса для загрузки данных.

        Возвращает JsonResponse с информацией об успешной загрузке данных.
        """
        # Дописать


class MainView(View):
    """
    Представление для отображения списка продуктов с возможностью фильтрации.

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
      - product_id: Идентификатор продукта.
    
    Возвращает JsonResponse со списком продуктов, в том числе удовлетворяющих заданным критериям фильтрации,
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
            Если параметр status_filter задан, устанавливает фильтр по статусу продуктов.

            Параметры:
            - status_filter (str): Фильтр по статусу ('matched' или 'unmatched').

            Действия:
            - Если status_filter равен 'matched', фильтрует продукты, у которых имеются соответствия.
            - Если status_filter равен 'unmatched', фильтрует продукты, у которых нет соответствий.

            Результат:
            - dealer_filter обновляется в соответствии с заданным статусом для последующего использования
            в фильтрации продуктов.
            """
            
            if status_filter == 'matched':
                dealer_filter['product_dealer_keys__isnull'] = False
            elif status_filter == 'unmatched':
                dealer_filter['product_dealer_keys__isnull'] = True

        # Получение списка продуктов из базы данных
        products_info_objects = Product.objects.filter(**dealer_filter)

        # Сериализация данных о товарах
        products_info_serialized = ProductSerializer(products_info_objects, many=True).data

        # Получение списка вариантов соответствия для каждого продукта
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
        product_id = request.POST.get('product_id')
        
        if action == 'Да':
            product = get_object_or_404(Product, id=product_id)
            product.is_matched = True
            product.save()
            return JsonResponse({"message": f"Продукт {product_id} подтвержден"})
        elif action == 'Нет':
            product = get_object_or_404(Product, id=product_id)
            product.is_matched = False
            product.save()
            return JsonResponse({"message": f"Продукт {product_id} не подтвержден"})
        elif action == 'Сопоставить':
            product = get_object_or_404(Product, id=product_id)
            matching_options_url = reverse('matching_options', args=[product_id])
            return JsonResponse({"message": f"Сопоставление продукта {product_id}", "matching_options_url": matching_options_url})
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
        # Здесь добавить логику для предоставления вариантов соответствия (с использованием ML-модели)

            
    
class MarkupProductView(View):
    """
    Представление для разметки товара.
    """

    template_name = 'заменить на будущий путь шаблона.html'  # Шаблон для режима разметки

    def get(self, request, product_id, *args, **kwargs):
        """
        Обработчик GET-запроса для отображения сохраненной разметки товара.

        Возвращает JsonResponse с информацией о разметке для указанного товара.
        """
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

    @transaction.atomic
    def post(self, request, product_id, *args, **kwargs):
        """
        Обработчик POST-запроса для разметки товара.

        Возвращает JsonResponse с информацией о завершении разметки и идентификатором разметки.
        """
        product = get_object_or_404(Product, id=product_id)
        markup_request_form = MarkupRequestForm(request.POST)

        if markup_request_form.is_valid():
            key = markup_request_form.cleaned_data['key']
            # Получаем уже размеченные варианты
            marked_options = ProductDealerKey.objects.filter(product=product)
            
            # Если есть размеченные варианты
            if marked_options.exists():
                # Проверяем, выбран ли вариант
                selected_option = marked_options.filter(key=key).first()
                
                if selected_option:
                    # Если выбран тот же вариант, что и ранее, снимаем выбор
                    selected_option.delete()
                else:
                    # Если выбран новый вариант, заменяем предыдущий
                    marked_options.update(key=None)
                    ProductDealerKey.objects.create(key=key, product=product, order=marked_options.count() + 1)
            else:
                # Если нет размеченных вариантов, просто создаем новый
                ProductDealerKey.objects.create(key=key, product=product, order=1)
            
            # Сохраняем статистику выбора варианта
            choice_statistics = Statistics.objects.create(
                product=product,
                chosen_option_order=marked_options.count() + 1,
            )
            response_data = {
                "message": f"Разметка товара {product_id} завершена",
                "choice_statistics": choice_statistics.id
            }

            # Получаем следующий неразмеченный продукт
            next_unmarked_product = Product.objects.filter(is_matched=False).first()

            if next_unmarked_product:
                # Если есть следующий неразмеченный продукт, добавляем его информацию в ответ
                response_data["next_unmarked_product_id"] = next_unmarked_product.id

            return JsonResponse(response_data)
        else:
            return JsonResponse({"error": "Неверные данные формы"}, status=400)


class StatisticsView(View):
    """
    Представление для работы со статистикой.
    """
    
    template_name = 'statistics.html'

    def get(self, request, *args, **kwargs):
        # Получаем начальную и конечную дату из запроса
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

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

        # Статистика по тому, как часто ни один вариант не выбран за выбранный период
        none_chosen_count = chosen_options_stats.filter(chosen_option_count=0).count()

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

        return render(request, self.template_name, context)
