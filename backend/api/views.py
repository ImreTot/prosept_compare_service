import json
from datetime import datetime, timedelta
import os

from django.db import transaction
from django.db.models import Case, CharField, Count, F, Value, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from products.models import Dealer, DealerPrice, Product, ProductDealerKey

from .forms import MarkupRequestForm
from .serializers import (DealerPriceSerializer, DealerSerializer,
                          ProductDealerKeySerializer, ProductSerializer)
from tools.import_csv import (import_dealers_from_csv,
                              import_products_from_csv,
                              import_prices_from_csv,
                              export_model_to_csv_binary,
                              save_json)
from ML.main_script import result

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
        prices_urls = {price.product_url: price for price in DealerPrice.objects.all()}
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


class MainView(View):
    def get(self, request, *args, **kwargs):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status_filter = request.GET.get('status')

        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=6)

        if not isinstance(start_date, datetime):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if not isinstance(end_date, datetime):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        filters = {'product_dealer_keys__key__marking_date__range': [start_date, end_date]}

        annotations = {
            'status': Case(
                When(product_dealer_keys__isnull=False, then=Value('matched')),
                default=Value('unmatched'),
                output_field=CharField()
            ),
            'matching_product_id': F('product_dealer_keys__product_id')
        }

        if status_filter:
            if status_filter == 'matched':
                filters['product_dealer_keys__isnull'] = False
            elif status_filter == 'unmatched':
                filters['product_dealer_keys__isnull'] = True

        products_info = Product.objects.filter(**filters).annotate(**annotations).values('id', 'article', 'name', 'status', 'matching_product_id')

        return JsonResponse({'products': list(products_info)})


class MatchingOptionsView(View):
    """
    Представление для получения вариантов соответствия товара.
    """

    def get(self, request, product_id, *args, **kwargs):
        """
        Обработчик GET-запроса для получения вариантов соответствия товара.

        Возвращает JsonResponse с вариантами соответствия (в данном случае, просто целыми числами).
        """
        # Здесь добавить логику для предоставления вариантов соответствия (с использованием ML-модели)
        recommendations = [1, 2, 3]  # Заменить на логику получения рекомендаций
        return JsonResponse({"product_id": product_id, "recommendations": recommendations})
    
    
class MarkupProductView(View):
    """
    Представление для разметки товара.
    """

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

    @method_decorator(csrf_exempt)
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
            # Получаем текущее количество разметок для товара
            markup_count = ProductDealerKey.objects.filter(product=product).count()
            
            # Увеличиваем счетчик для новой разметки
            product_dealer_key = ProductDealerKey.objects.create(key=key, product=product, order=markup_count + 1)
            return JsonResponse({"message": f"Разметка товара {product_id} завершена", "markup_id": product_dealer_key.id})
        else:
            return JsonResponse({"error": "Неверные данные формы"}, status=400)


class StatisticsView(TemplateView):
    template_name = 'statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем начальную и конечную дату из запроса
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        # Используем даты из запроса или значения по умолчанию
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=6)

        # Преобразуем строки в объекты дат
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Получение общего количества размеченных товаров за выбранный период
        total_markup_count = ProductDealerKey.objects.filter(
            marking_date__range=[start_date, end_date]
        ).count()

        # Получение статистики выбора предложенных вариантов за выбранный период
        chosen_options_stats = ProductDealerKey.objects.filter(
            marking_date__range=[start_date, end_date]
        ).exclude(key=None).values(
            'product_id', 'dealer_id', 'product_id__category_id'
        ).annotate(
            total_choices=Count('id'),
            chosen_option_count=Count('key')
        )

        # Получение статистики по порядку выбора вариантов за выбранный период
        choices_order_stats = chosen_options_stats.values(
            'choices_order', 'product_id', 'dealer_id', 'product_id__category_id'
        ).annotate(
            choices_count=Count('choices_order')
        ).order_by('choices_order')

        # Статистика по тому, как часто ни один вариант не выбран за выбранный период
        none_chosen_count = chosen_options_stats.filter(chosen_option_count=0).count()

        context['start_date'] = start_date.strftime("%Y-%m-%d")
        context['end_date'] = end_date.strftime("%Y-%m-%d")
        context['total_markup_count'] = total_markup_count
        context['chosen_options_stats'] = chosen_options_stats
        context['choices_order_stats'] = choices_order_stats
        context['none_chosen_count'] = none_chosen_count

        return context
