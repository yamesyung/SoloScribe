from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    latitude = models.CharField(max_length=50, null=True)
    longitude = models.CharField(max_length=50, null=True)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class City(models.Model):
    city_name = models.CharField(max_length=200)
    admin_name = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200)
    code = models.CharField(max_length=2)
    latitude = models.CharField(max_length=50, null=True)
    longitude = models.CharField(max_length=50, null=True)
    population = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.city_name
