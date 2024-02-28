from django.contrib import admin

from .models import Country, City


class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "latitude", "longitude")


admin.site.register(Country, CountryAdmin)


class CityAdmin(admin.ModelAdmin):
    list_display = ("city_name", "admin_name", "country", "code", "latitude", "longitude")


admin.site.register(City, CityAdmin)
