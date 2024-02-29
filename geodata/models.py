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


class Region(models.Model):
    region_name = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    combined_name = models.CharField(max_length=200)
    latitude = models.CharField(max_length=50, null=True)
    longitude = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.region_name


class City(models.Model):
    city_name = models.CharField(max_length=200)
    city_name_ascii = models.CharField(max_length=200)
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


class Place(models.Model):
    """
    for all other locations that exists and are not in the local database
    verify on map or add approximate coordinates
    https://nominatim.openstreetmap.org/ui/search.html
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200, null=True)
    latitude = models.CharField(max_length=50, null=True)
    longitude = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name
