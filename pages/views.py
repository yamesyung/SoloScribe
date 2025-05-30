import random
import calendar
from datetime import datetime, date
from collections import defaultdict

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from accounts.views import get_current_theme
from books.models import Book, Review, Quote


def homepage(request):
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day

    cal = calendar.monthcalendar(year, month)

    month_name = calendar.month_name[month]
    current_month = date.today().month

    event_days = set()
    event_days.update(Review.objects.filter(date_read__month=month)
                      .values_list('date_read__day', flat=True))

    event_days.update(Quote.objects.filter(date_added__month=month)
                      .values_list('date_added__day', flat=True))

    event_days = list(event_days)

    currently_reading_list = Book.objects.filter(review__bookshelves="currently-reading")

    active_theme = get_current_theme()
    context = {'calendar': cal, 'month_name': month_name, 'year': year, 'current_day': day,
               'event_days': event_days, 'month': current_month, 'current_month': current_month,
               'currently_reading_list': currently_reading_list, 'active_theme': active_theme}

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
    books = Book.objects.filter(review__bookshelves='to-read')[:2]
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


def display_book_events(request):
    day = request.GET.get('day')
    month = request.GET.get('month')
    month_name = calendar.month_name[int(month)]

    books = (Book.objects.filter(review__date_read__day=day, review__date_read__month=month)
             .values('title', 'review__date_read__year', 'goodreads_id').order_by('-review__date_read__year'))

    grouped_books = defaultdict(list)
    for book in books:
        year = book['review__date_read__year'] or 'Unknown'
        grouped_books[year].append(book)

    grouped_books = dict(sorted(grouped_books.items(), reverse=True))

    quotes = (Quote.objects.filter(date_added__day=day, date_added__month=month)
              .values('text', 'date_added__year', 'book__title', 'book__goodreads_id').order_by('-date_added__year'))

    grouped_quotes = defaultdict(list)
    for quote in quotes:
        year = quote['date_added__year'] or 'Unknown'
        grouped_quotes[year].append(quote)

    grouped_quotes = dict(sorted(grouped_quotes.items(), reverse=True))

    context = {'day': day, 'month_name': month_name, 'grouped_books': grouped_books, 'grouped_quotes': grouped_quotes}
    return render(request, 'partials/homepage/book_events.html', context)


def calendar_view(request):
    current_year = date.today().year
    month = int(request.GET.get('month', date.today().month))
    year = current_year

    month_name = calendar.month_name[month]
    _, num_days = calendar.monthrange(year, month)

    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdayscalendar(year, month)

    event_days = set()
    event_days.update(Review.objects.filter(date_read__month=month).values_list('date_read__day', flat=True))
    event_days.update(Quote.objects.filter(date_added__month=month).values_list('date_added__day', flat=True))
    event_days = list(event_days)

    context = {
        "calendar": weeks,
        "year": year,
        "month": month,
        "month_name": month_name,
        "event_days": event_days,
        "current_day": date.today().day,
        "current_month": date.today().month,
    }

    return render(request, 'partials/homepage/calendar.html', context)
