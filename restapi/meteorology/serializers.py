from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from meteorology.models import ClimaticCondition, City


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        exclude = ('id',)


class ClimaticConditionSerializer(serializers.Serializer):
    city_name = serializers.CharField(max_length=100, required=False, allow_null=True)
    city_code = serializers.IntegerField(required=False, allow_null=True, min_value=1)

    def validate(self, attrs):
        fields = attrs.get('city_name'), (attrs.get('city_code'))
        if all(fields):
            raise ValidationError('You can enter one of code/name of city!')
        if not any(fields):
            raise ValidationError('Enter name/code of city. (one of them)')
        return attrs


class ClimaticConditionResponse(serializers.ModelSerializer):
    city_detail = CitySerializer(source='city')

    class Meta:
        model = ClimaticCondition
        fields = ('main', 'description', 'temp', 'temp_max', 'temp_min', 'pressure', 'date', 'city_detail',)
