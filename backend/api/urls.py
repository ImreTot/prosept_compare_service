from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (LoadDataView, MainView, MarkupProductView,
                    MatchingOptionsView, StatisticsView)

# Создаем роутер
router = DefaultRouter()

urlpatterns = [
    path('', MainView.as_view(), name='main_view'),
    path('load_data/', LoadDataView.as_view(), name='load_data'),
    path('matching_options/<int:product_id>/', MatchingOptionsView.as_view(), name='matching_options'),
    path('markup_product/<int:product_id>/', MarkupProductView.as_view(), name='markup_product'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('api/v1/', include(router.urls)),
]
