from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.IntegerField(unique=True)


class ClimaticCondition(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    main = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    temp = models.FloatField(help_text='main temperature')
    temp_min = models.FloatField(help_text='minimum temperature')
    temp_max = models.FloatField(help_text='maximum temperature')
    pressure = models.IntegerField()
    date = models.DateField(auto_now=True)

    @classmethod
    def fields(cls):
        remove_extra = lambda s: s.replace(f'{cls._meta.app_label}.{cls.__name__}.', '')
        fields = map(remove_extra, map(str, cls._meta.fields))
        return set(fields)
