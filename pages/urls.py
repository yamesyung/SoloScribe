from django.urls import path

from .views import HomePageView, AboutPageView, changelog, pikabook, replace_cover

urlpatterns = [
    path("about/", AboutPageView.as_view(), name="about"),
    path("", HomePageView.as_view(), name="home"),
]

htmx_urlpatterns = [
    path("changelog/", changelog, name="changelog"),
    path("pikabook/", pikabook, name="pikabook"),
    path('replace-cover/<int:book_id>/', replace_cover, name='replace_cover'),
]

urlpatterns += htmx_urlpatterns
