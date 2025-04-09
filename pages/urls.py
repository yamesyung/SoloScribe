from django.urls import path

from .views import homepage, AboutPageView, changelog, pikabook, replace_cover, display_book_events, calendar_view

urlpatterns = [
    path("about/", AboutPageView.as_view(), name="about"),
    path("", homepage, name="home"),
]

htmx_urlpatterns = [
    path("changelog/", changelog, name="changelog"),
    path("pikabook/", pikabook, name="pikabook"),
    path('replace-cover/<int:book_id>/', replace_cover, name='replace_cover'),
    path('calendar-view/', calendar_view, name='calendar_view'),
    path("display-book-events/", display_book_events, name="display_book_events"),
]

urlpatterns += htmx_urlpatterns
