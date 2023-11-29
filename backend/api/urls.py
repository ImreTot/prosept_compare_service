from django.urls import path
from .views import LoadDataView, MainView, MatchingOptionsView, MarkupProductView, StatisticsView

urlpatterns = [
    path('load_data/', LoadDataView.as_view(), name='load_data'),
    path('main_view/', MainView.as_view(), name='main_view'),
    path('matching_options/<int:product_id>/', MatchingOptionsView.as_view(), name='matching_options'),
    path('markup_product/<int:product_id>/', MarkupProductView.as_view(), name='markup_product'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
]