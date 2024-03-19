from django.contrib import admin
from .models import Book, RecList, Genre, Location, BookList


class RecListFilter(admin.SimpleListFilter):
    title = 'Recommendation List'
    parameter_name = 'rec_list'

    def lookups(self, request, model_admin):
        # Fetch distinct list_ids from BookList
        list_ids = BookList.objects.values_list('list_id', flat=True).distinct()
        rec_lists = RecList.objects.filter(id__in=list_ids)
        return [(rec_list.id, rec_list.name) for rec_list in rec_lists]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(booklist__list_id=self.value()).order_by('-rating_counts')


class BookAdmin(admin.ModelAdmin):
    list_display = ("goodreads_id", "title", "author")
    search_fields = ("title", "author")
    list_filter = (RecListFilter,)


admin.site.register(Book, BookAdmin)


class RecListAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "category")
    search_fields = ("name", "type", "category")
    list_filter = ("type", "category")


admin.site.register(RecList, RecListAdmin)


class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(Genre, GenreAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ["name"]


admin.site.register(Location, LocationAdmin)