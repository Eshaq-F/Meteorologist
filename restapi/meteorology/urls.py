from django.urls import path
from meteorology.views import GetClimaticCondition, ListCity


app_name = 'meteorology'

urlpatterns = [
    path('get-climatic-condition/', GetClimaticCondition.as_view(), name='get_climatic_condition'),
    path('list-city/', ListCity.as_view(), name='list_city'),
]