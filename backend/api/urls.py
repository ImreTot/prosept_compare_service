from django.urls import path
from .views import LoadDataView, MainView

urlpatterns = [
    path('load_data/', LoadDataView.as_view(), name='load_data'),
    path('', MainView.as_view(), name='main_view'),
]