from logging import getLogger
from requests import get as get_request
from django.utils.timezone import now
from django.core.cache import cache
from django.db.transaction import atomic
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from meteorology.serializers import ClimaticConditionSerializer, ClimaticConditionResponse, CitySerializer
from meteorology.models import City, ClimaticCondition
from project.exceptions import ServiceUnavailableError

logger  = getLogger(__name__)

class GetClimaticCondition(APIView):
    serializer_class = ClimaticConditionSerializer

    @swagger_auto_schema(operation_description="Return current climatic condition of the input city.",
                         responses={
                             200: ClimaticConditionResponse,
                             400: 'BAD REQUEST',
                             404: 'NOT FOUND',
                             503: 'SERVICE NOT AVAILABLE'
                         }, query_serializer=serializer_class, security=[])
    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.GET)
        serializer.is_valid(raise_exception=True)
        city = {'name': city_name.lower()} if (city_name := serializer.validated_data.get('city_name')) else {
            'code': serializer.validated_data.get('city_code')}
        setattr(self, 'city', city)
        response_ser = ClimaticConditionResponse(self.get_object())
        return Response(response_ser.data, status=status.HTTP_200_OK)

    def get_object(self):
        city_obj = City.objects.filter(**self.city).last()
        if city_obj:
            if climatic_obj := cache.get(city_obj.name):
                return climatic_obj
            if climatic_obj:= ClimaticCondition.objects.filter(city=city_obj, date=now().date()).last():
                cache.set(city_obj.name, climatic_obj, 60 * 60 * 12)
                return climatic_obj
        if not city_obj and not self.city.get('name'):
            raise ParseError('Must Enter name to add new city!')
        try:
            city_name = self.city.get('name') or city_obj.name
            return GetClimaticCondition.provider_api_call(city=city_name)
        except NotFound:
            raise
        except Exception as e:
            logger.exception(e)
            raise ServiceUnavailableError('Meteorology provider is not responding!')

    @staticmethod
    def provider_api_call(city=None):
        params = {'q': city, 'appid': settings.PROVIDER_TOKEN}
        response = get_request(settings.PROVIDER_URL, params=params, verify=False)
        if response.status_code == status.HTTP_200_OK:
            climatic_obj = GetClimaticCondition.create_objects(response.json())
            cache.set(climatic_obj.city.name, climatic_obj, 60 * 60 * 12)
            return climatic_obj
        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise NotFound('Given city was not found')

    @staticmethod
    def create_objects(data):
        city_data = {'name': data.get('name'), 'code': data.get('id')}
        climate_data = {k: v for k, v in data.get('weather', [])[0].items() if k in ClimaticCondition.fields()}
        climate_data.update({k: v for k, v in data.get('main', {}).items() if k in ClimaticCondition.fields()})
        with atomic():
            city = City.objects.get_or_create(**city_data)[0]
            climatic_obj = ClimaticCondition.objects.create(city=city, **climate_data)
        return climatic_obj


class ListCity(ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer