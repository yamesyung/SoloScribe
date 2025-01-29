import random
import calendar
from datetime import datetime

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from accounts.views import get_current_theme
from books.models import Book, Review


def homepage(request):
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day

    cal = calendar.monthcalendar(year, month)

    month_name = calendar.month_name[month]

    event_days = set()
    event_days.update(Review.objects.filter(date_read__month=month)
                      .values_list('date_read__day', flat=True))

    event_days = list(event_days)

    active_theme = get_current_theme()
    print(event_days)
    context = {'calendar': cal, 'month_name': month_name, 'year': year, 'current_day': day,
               'event_days': event_days, 'active_theme': active_theme}

    return render(request, 'home.html', context)


class AboutPageView(TemplateView):
    template_name = "about.html"


def changelog(request):
    """
    renders a partial containing the  changelog
    """
    return render(request, 'partials/homepage/changelog.html')


def pikabook(request):
    """
    start of a homepage minigame where you have to choose between 2 books based on your own criteria.
    Can add animations, related model for scores or whatever. Hidden for now.
    """
    books = Book.objects.filter(review__bookshelves='dnf')[:2]
    context = {'books': books}
    return render(request, 'partials/homepage/pikabook.html', context)


def replace_cover(request, book_id):
    """
    see above
    """
    selected_book = get_object_or_404(Book, goodreads_id=book_id)
    other_books = Book.objects.exclude(goodreads_id=book_id)
    random_book = random.choice(other_books) if other_books.exists() else None

    books = [selected_book]
    if random_book:
        books.append(random_book)
    return render(request, "partials/homepage/pikabook.html", {"books": books})


def current_month_calendar(request):
    now = datetime.now()
    year = now.year
    month = now.month

    cal = calendar.monthcalendar(year, month)

    month_name = calendar.month_name[month]

    context = {'calendar': cal, 'month_name': month_name, 'year': year}

    return render(request, 'partials/homepage/calendar.html', context)
