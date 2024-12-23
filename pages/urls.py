from django.urls import path

from .views import HomePageView, AboutPageView, changelog

urlpatterns = [
    path("about/", AboutPageView.as_view(), name="about"),
    path("", HomePageView.as_view(), name="home"),
]

htmx_urlpatterns = [
    path("changelog/", changelog, name="changelog"),
]

urlpatterns += htmx_urlpatterns
