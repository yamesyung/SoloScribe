from django.shortcuts import render
from django.views.generic import TemplateView

from accounts.views import get_current_theme


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_theme'] = get_current_theme()
        return context


class AboutPageView(TemplateView):
    template_name = "about.html"


def changelog(request):
    return render(request, 'partials/homepage/changelog.html')
