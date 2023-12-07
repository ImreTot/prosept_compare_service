from datetime import date, datetime, timedelta

from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
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

    template_name = 'main_view.html'

    def get(self, request, *args, **kwargs):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status_filter = request.GET.get('status')
        dealer_ids = request.GET.getlist('dealers[]')
        num_matches = request.GET.get('num_matches')

        # Дополнительная фильтрация по dealer_ids
        dealer_filter = {}
        if dealer_ids:
            dealer_filter['dealer__id__in'] = dealer_ids

        # Получение списка продавцов
        dealers = Dealer.objects.filter(**dealer_filter)

        # Фильтрация по дате
        date_filter = {}

        # Фильтрация по статусу
        status_filter_query = Q()

        if status_filter:
            if status_filter == 'matched':
                status_filter_query &= Q(product_dealer_keys__isnull=False)
            elif status_filter == 'unmatched':
                status_filter_query &= Q(product_dealer_keys__isnull=True)

        # Объединяем все фильтры
        all_filters = Q(**date_filter) & status_filter_query
        products_info_objects = Product.objects.filter(all_filters).distinct()

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
            num_matches = int(num_matches)
            matching_options = matching_options[:num_matches]

        # Сериализация цен продавцов
        dealer_prices = DealerPrice.objects.filter(dealer_id__in=dealers, **dealer_filter)
        dealer_prices_serialized = DealerPriceSerializer(dealer_prices, many=True).data

        # Сериализация данных о продавцах
        dealers_serialized = DealerSerializer(dealers, many=True).data

        return render(request, self.template_name, {
            'products': products_info_serialized,
            'matching_options': matching_options,
            'dealer_prices': dealer_prices_serialized,
            'dealers': dealers_serialized,
            'product_id': product_key,
        })
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        product_id = request.POST.get('product_id')

        try:
            product_id = int(product_id)
            product = get_object_or_404(Product, id=product_id)

            if action == 'Да':
                product.is_matched = True
                product.save()
                return render(request, self.template_name, {"message": f"Товар {product_id} подтвержден"})
            elif action == 'Нет':
                product.is_matched = False
                product.save()
                return render(request, self.template_name, {"message": f"Товар {product_id} не подтвержден"})
            elif action == 'Сопоставить':
                try:
                    dealer_price = DealerPrice.objects.get(product_key=product_id)
                except DealerPrice.DoesNotExist:
                    return JsonResponse({"error": "DealerPrice не найден для указанного product_key"}, status=400)
    
                matching_options_url = reverse('matching_options', args=[dealer_price.product_id_id])
                return render(request, self.template_name, {"message": f"Сопоставление товара {product_id}", "matching_options_url": matching_options_url})
            else:
                return JsonResponse({"error": "Неверное действие"}, status=400)
        except (ValueError, Product.DoesNotExist):
            return JsonResponse({"error": "Invalid product ID"}, status=400)
    

class MatchingOptionsView(View):
    """
    Представление для получения вариантов соответствия товара.
    """

    def get(self, product_id):
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
    template_name = 'markup.html'

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
    
    template_name = 'statistics.html'

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

        return render(request, self.template_name, context)


class VariantStatisticsView(View):
    """
    Представление для статистики по номеру варианта.
    """

    template_name = 'variant_statistics.html'

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

        return render(request, self.template_name, context)
