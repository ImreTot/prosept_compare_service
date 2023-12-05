from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DealerListCreateView, DealerPriceListCreateView,
                    LoadDataView, MainView, MarkupProductView,
                    MatchingOptionsView, ProductDealerKeyListCreateView,
                    ProductListCreateView, StatisticsView, VariantStatisticsView)

# Создаем роутер
router = DefaultRouter()
router.register('dealers', DealerListCreateView, basename='dealers')
router.register('products', ProductListCreateView, basename='products')
router.register('dealer_prices', DealerPriceListCreateView, basename='dealer_prices')
router.register('product_dealer_keys', ProductDealerKeyListCreateView, basename='product_dealer_keys')

urlpatterns = [
    path('', MainView.as_view(), name='main_view'),
    path('load_data/', LoadDataView.as_view(), name='load_data'),
    path('matching_options/<int:product_id>/', MatchingOptionsView.as_view(), name='matching_options'),
    path('markup_product/<int:product_id>/', MarkupProductView.as_view(), name='markup_product'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('variant_statistics/', VariantStatisticsView.as_view(), name='variant_statistics'),
    path('api/v1/', include(router.urls)),
]
