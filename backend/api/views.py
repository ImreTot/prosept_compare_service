from django.http import JsonResponse
from products.models import Dealer, Product, DealerPrice, ProductDealerKey
from .forms import MarkupRequestForm
from rest_framework import generics
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.db import transaction
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from .serializers import DealerSerializer, ProductSerializer, DealerPriceSerializer, ProductDealerKeySerializer
from django.db.models import Count, F, Case, When, Value, CharField


class DealerListCreateView(generics.ListCreateAPIView):
    queryset = Dealer.objects.all()
    serializer_class = DealerSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class DealerPriceListCreateView(generics.ListCreateAPIView):
    queryset = DealerPrice.objects.all()
    serializer_class = DealerPriceSerializer


class ProductDealerKeyListCreateView(generics.ListCreateAPIView):
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
    def get(self, request, *args, **kwargs):
        # Получаем параметры фильтрации из запроса
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status_filter = request.GET.get('status') # Есть сопоставление с товаром производителя или нет

        # Используем даты из запроса или значения по умолчанию
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=6)

        # Преобразуем строки в объекты дат
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Формируем фильтры для запроса
        filters = {'product_dealer_keys__marking_date__range': [start_date, end_date]}
        if status_filter:
            if status_filter == 'matched':
                filters['product_dealer_keys__key__isnull'] = False
            elif status_filter == 'unmatched':
                filters['product_dealer_keys__key__isnull'] = True

        # Получаем данные о товарах продавцов с учетом фильтров
        products_info = Product.objects.annotate(
            status=Case(
                When(product_dealer_keys__marking_date__range=[start_date, end_date], then=Value('matched')),
                default=Value('unmatched'),
                output_field=CharField()
            ),
            matching_product_id=Case(
                When(product_dealer_keys__marking_date__range=[start_date, end_date], then=F('product_dealer_keys__product_id')),
                default=None,
                output_field=CharField()
            )
        ).filter(**filters).values('id', 'article', 'name', 'status', 'matching_product_id')

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
