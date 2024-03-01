from django.contrib import admin

from .models import Country, City, Region, Place


class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "latitude", "longitude")
    search_fields = ("name", "code")


admin.site.register(Country, CountryAdmin)


class RegionAdmin(admin.ModelAdmin):
    list_display = ("region_name", "country", "code", "latitude", "longitude")
    search_fields = ("region_name", "country", "code")
    list_filter = ["country"]


admin.site.register(Region, RegionAdmin)


class CityAdmin(admin.ModelAdmin):
    list_display = ("city_name", "admin_name", "country", "code", "latitude", "longitude", "population")
    search_fields = ("city_name", "admin_name", "country", "code")
    list_filter = ["country"]


admin.site.register(City, CityAdmin)


class PlacesAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")


admin.site.register(Place, PlacesAdmin)
