import os
import ast
import json
import spacy
import pandas as pd
from collections import Counter, defaultdict
from html import unescape
from datetime import datetime

from django.conf import settings
from django.urls import reverse
from django.utils.html import escape
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.db.models import Q, Value, Count, F, Prefetch, Sum, Avg, CharField
from django.db.models.functions import Concat, ExtractYear, ExtractMonth, Cast, Coalesce
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse

from .models import (Book, Author, Review, Award, Genre, BookGenre, Location, BookLocation, AuthorNER, AuthorLocation,
                     AuthLoc, UserTag, ReviewTag, Quote, QuoteTag, QuoteQuoteTag)
from geodata.models import Country, City, Region, Place


def remove_subset(a):
    """
    function used to clean scraped data: author's influences
    it is common it contains substrings of author's name
    """
    return [x for x in a if not any(x in y and x != y for y in a)]


def clear_empty_lists(x):
    """
    function used to clean scraped data: author's list
    I want list data type to be stored in the database as a string with a python list form,
    so I can process it later using abstract syntax trees
    """
    if x == ['[', ']']:
        return []
    else:
        return x


def remove_more_suffix(text):
    """
    function used to remove scraped data: author's description
    it is common to end with '...more'
    """
    if text.endswith("...more"):
        return text[:-8]
    else:
        return text


def format_date(date):
    """
    function used to process date fields when importing the csv file
    """
    return datetime.strptime(date, '%Y/%m/%d').strftime('%Y-%m-%d')


def clean_author_description(text):
    """
    function used to clean scraped data: author's description
    it is common to repeat itself after 750 characters OR so
    """
    pattern = text[:100]

    first_occurrence_index = text.find(pattern)
    if first_occurrence_index != -1:
        second_occurrence_index = text.find(pattern, first_occurrence_index + len(pattern))

        if second_occurrence_index != -1:
            return text[:first_occurrence_index] + text[second_occurrence_index:]

    return text


@login_required()
def author_list(request):
    """
    Show authors of books reviewed by the current user's profile
    """
    user_profile = request.user

    authors = (
        Author.objects.filter(book__review__user=user_profile)
        .annotate(book_count=Count("book", distinct=True))
        .distinct()
        .order_by("name")
    )

    formatted_authors = []
    for author in authors:
        birth = ""
        death = ""

        if author.birth_date and author.birth_date.year != 1:
            birth = author.birth_date.strftime("%d-%m-%Y")

        if author.death_date and author.death_date.year != 1:
            death = author.death_date.strftime("%d-%m-%Y")

        formatted_authors.append({
            "author_id": author.author_id,
            "name": author.name,
            "birth_date": birth,
            "death_date": death,
            "avg_rating": author.avg_rating,
            "ratings_count": author.ratings_count,
            "reviews_count": author.reviews_count,
            "genres": ast.literal_eval(author.genres) if isinstance(author.genres, str) else author.genres or [],
            "book_count": getattr(author, "book_count", 0),
        })

    context = {"author_list": formatted_authors}
    return render(request, "authors/author_list.html", context)


@login_required()
def timeline(request):
    """
    function used to render the timeline view
    It filters authors with unknown birthdate(0001-01-01)
    treats the authors with unknown death date(0001-01-01) as currently alive in the .js file
    need testing with negative values
    """
    user = request.user
    author_data = (
        Author.objects.filter(
            Q(book__review__user=user), birth_date__year__gt=1).distinct().values('name', 'birth_date', 'death_date'))

    for person in author_data:
        person['birth_date'] = Author.convert_date_string(person['birth_date'])
        person['death_date'] = Author.convert_date_string(person['death_date'])

    context = {'people_data': list(author_data)}
    return render(request, "authors/author_timeline.html", context)


@login_required()
def author_graph(request):
    """
    function used to render the graph view
    it uses ast to process strings in the form of python lists
    optional: filter data by read/to-read authors; add option to exclude authors with no influences
    """
    user = request.user
    data = (Author.objects.filter(Q(book__review__user=user), Q(name__isnull=False), ~Q(name=""))
            .distinct().values('name', 'influences'))

    for person in data:
        person['influences'] = ast.literal_eval(person['influences'])

    context = {'data': list(data)}
    return render(request, "authors/author_graph.html", context)


@login_required()
def author_graph_3d(request):
    """
    function used to render the graph view
    it uses ast to process strings in the form of python lists
    """
    user = request.user
    data = (Author.objects.filter(Q(book__review__user=user), Q(name__isnull=False), ~Q(name=""))
            .distinct().values('name', 'influences'))

    unique_nodes = set()
    nodes = []
    edges = []

    for person in data:
        person['influences'] = ast.literal_eval(person['influences'])

        # Add node for the current author
        author_node_id = f"author_{person['name']}"
        if author_node_id not in unique_nodes:
            nodes.append({"id": author_node_id, "name": person['name']})
            unique_nodes.add(author_node_id)

        # Add nodes for the influenced authors
        for influence_name in person['influences']:
            influence_node_id = f"author_{influence_name}"
            if influence_node_id not in unique_nodes:
                nodes.append({"id": influence_node_id, "name": influence_name})
                unique_nodes.add(influence_node_id)

            # Add edge from the current author to the influenced author
            edges.append({"source": author_node_id, "target": influence_node_id})

    graph_data = {
        "nodes": nodes,
        "links": edges,
    }

    context = {'graph_data': graph_data}
    return render(request, "authors/author_graph_3d.html", context)


@login_required()
def author_detail(request, pk):
    user = request.user
    author = get_object_or_404(Author, pk=pk)

    shelved_books = (
        Review.objects
        .filter(
            user=user,
            book__author=author
        )
        .values(
            'book__goodreads_id',
            'book__title',
            'original_publication_year',
            'bookshelves',
            'rating',
            'book__cover_local_path'
        )
        .order_by('original_publication_year')
    )

    context = {
        "author": author,
        "shelved_books": shelved_books,
    }

    return render(request, "authors/author_detail.html", context)


def delete_author(request, author_id):
    if request.method == "POST":
        author = get_object_or_404(Author, author_id=author_id)
        author.delete()

        return redirect('author_list')

    return redirect('author_list')


@login_required()
def search_results(request):
    """
    Search books by title or author name, limit to 30 results,
    and only include books with reviews from the current user.
    """
    query = request.GET.get("q", "")
    user = request.user

    books = (
        Book.objects.filter(
            (Q(title__icontains=query) | Q(author_text__icontains=query)) &
            Q(review__user=user)
        )
        .order_by('-review__date_added')
        .distinct()[:30]
    )

    context = {
        "book_list": books,
        "query": query,
    }

    return render(request, "books/search_results.html", context)


def clear_user_data(request):
    """
    function used to delete user's data (goodreads file)
    """
    Review.objects.all().delete()
    Book.objects.filter(scrape_status=False).delete()
    UserTag.objects.all().delete()

    return redirect("import_csv")


def delete_all_quotes(request):
    """
    function used to delete all quotes and set scraped quotes to false
    """
    Quote.objects.all().delete()
    Book.objects.filter(scraped_quotes=True).update(scraped_quotes=False)

    return redirect("import_csv")


def clear_scraped_data(request):
    """
    function used to delete the scraped data, book covers not included
    """
    Author.objects.all().delete()
    Award.objects.all().delete()
    Genre.objects.all().delete()
    BookGenre.objects.all().delete()
    Location.objects.all().delete()
    BookLocation.objects.all().delete()
    Book.objects.all().delete()
    AuthorLocation.objects.all().delete()
    AuthLoc.objects.all().delete()

    return redirect("import_csv")


def export_csv(request):
    """
    renders the export page, with csv and zip options
    """
    return render(request, "account/export_csv.html")


def export_csv_goodreads(request):
    """
    creates a csv file containing updated data with a similar format to the goodreads export library's file.
    Theoretically, you can import it back to goodreads, but it is not reliable (goodreads import problems)
    """

    queryset = Review.objects.all()

    data = []

    for review in queryset:
        tags = ", ".join(review_tag.tag.name for review_tag in ReviewTag.objects.filter(review=review))
        data.append({
            'Book Id': review.id,
            'Title': review.title,
            'Author': review.author,
            'Author l-f': review.author_lf,
            'Additional Authors': review.additional_authors,
            'ISBN': review.isbn,
            'ISBN13': review.isbn13,
            'My Rating': review.rating,
            'Average Rating': review.average_rating,
            'Publisher': review.publisher,
            'Binding': review.binding,
            'Number of Pages': review.number_of_pages,
            'Year Published': review.year_published,
            'Original Publication Year': review.original_publication_year,
            'Date Read': review.date_read.strftime('%Y/%m/%d') if review.date_read else None,
            'Date Added': review.date_added.strftime('%Y/%m/%d') if review.date_added else None,
            'Bookshelves': tags,
            'Bookshelves with positions': review.user_shelves_positions,  # I didn't bother here, doubt anyone needs it
            'Exclusive Shelf': review.bookshelves,
            'My Review': review.review_content,
            'Spoiler': review.spoiler,
            'Private Notes': review.private_notes,
            'Read Count': review.read_count,
            'Owned Copies': review.owned_copies,

        })
    df = pd.DataFrame(data)

    csv_buffer = df.to_csv(index=False).encode('utf-8')

    response = HttpResponse(csv_buffer, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reviews.csv"'
    return response


@login_required()
def book_list(request):
    """
    function used to display a table containing all imported books
    it uses the above SQL query to get data from all 3 tables, using joins
    I also added lower and regexp, had issues with authors like Stephen King and John le Carré
    """
    user = request.user
    books = (
        Book.objects
        .filter(review__user=user)
        .select_related('author')  # get author in same query
        .prefetch_related(
            Prefetch('review_set', queryset=Review.objects.filter(user=user)),
        )
        .distinct()
    )
    for book in books:
        book.review = book.review_set.first()

    context = {'book_list': books}

    return render(request, "books/book_list.html", context)


@login_required()
def book_detail(request, pk):
    """
    function used to display book detail page.
    """
    user = request.user
    book = get_object_or_404(
        Book.objects.select_related('author'),
        goodreads_id=pk
    )
    review = Review.objects.filter(user=user, book=book).first()
    quotes_number = Quote.objects.filter(review__user=user, review__book=book).count()
    rating_range = range(5, 0, -1)

    genres = Genre.objects.filter(bookgenre__goodreads_id=book)
    tags = UserTag.objects.filter(reviewtag__review=review)
    places = Location.objects.filter(booklocation__goodreads_id=book)

    shelves = (
        Review.objects
        .filter(user=user)
        .values('bookshelves')
        .annotate(num_books=Count('id'))
        .order_by('-num_books')
    )

    context = {'book': book, 'review': review, 'quotes_no': quotes_number, 'rating_range': rating_range,
               'gallery_shelves': shelves, 'genres': genres, 'tags': tags, 'places': places}

    return render(request, "books/book_detail.html", context)


def edit_book_form(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    book = review.book

    genres = Genre.objects.filter(bookgenre__goodreads_id=book)
    tags = UserTag.objects.filter(reviewtag__review__book=book)

    context = {'book': book, 'review': review, 'genres': genres, 'tags': tags}

    return render(request, 'partials/books/book_detail/edit_book_form.html', context)


def save_book_edit(request, review_id):
    if request.method == "POST":
        review = Review.objects.get(id=review_id)
        book = review.book

        # replace the cover
        if request.FILES.get('new-book-cover'):
            uploaded_file = request.FILES['new-book-cover']
            file_extension = os.path.splitext(uploaded_file.name)[1]

            if file_extension == ".jpg":
                filename = f'{book.goodreads_id}{file_extension}'

                static_dir = os.path.join(settings.BASE_DIR, 'media', 'book_covers')
                file_path = os.path.join(static_dir, filename)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                if not book.cover_local_path:
                    book.cover_local_path = os.path.join('book_covers', filename)
                    book.save()

        # replace the description
        description = request.POST.get("description-form", "")
        book.description = description
        book.save()

        # manage genres
        genres_json = request.POST.get("genres", '[]')
        try:
            genres_data = json.loads(genres_json) if genres_json else []
        except json.JSONDecodeError:
            return HttpResponse("Invalid tags format", status=400)

        current_genres = set(Genre.objects.filter(bookgenre__goodreads_id=book).values_list('name', flat=True))

        genre_names = {tag['value'].strip() for tag in genres_data if 'value' in tag}

        genres_to_add = genre_names - current_genres
        genres_to_remove = current_genres - genre_names

        for genre_name in genres_to_add:
            genre_obj, _ = Genre.objects.get_or_create(name=genre_name)
            BookGenre.objects.create(goodreads_id=book, genre_id=genre_obj)

        for genre_name in genres_to_remove:
            try:
                genre_obj = Genre.objects.get(name=genre_name)
                BookGenre.objects.filter(goodreads_id=book, genre_id=genre_obj).delete()
            except Genre.DoesNotExist:
                continue

        # manage user tags
        tags_json = request.POST.get("tags", '[]')

        try:
            tags_data = json.loads(tags_json) if tags_json else []
        except json.JSONDecodeError:
            return HttpResponse("Invalid tags format", status=400)

        current_tags = set(review.reviewtag_set.values_list('tag__name', flat=True))

        tag_names = {tag['value'].strip() for tag in tags_data if 'value' in tag}

        tags_to_add = tag_names - current_tags
        tags_to_remove = current_tags - tag_names

        for tag_name in tags_to_add:
            user_tag, created = UserTag.objects.get_or_create(name=tag_name)
            ReviewTag.objects.create(review=review, tag=user_tag)

        for tag_name in tags_to_remove:
            try:
                user_tag = UserTag.objects.get(name=tag_name)
                ReviewTag.objects.filter(review=review, tag=user_tag).delete()
            except Genre.DoesNotExist:
                continue

        return redirect('book_detail', pk=book.goodreads_id)

    review = Review.objects.get(id=review_id)
    book = review.book
    return redirect('book_detail', pk=book.goodreads_id)


def book_detail_quotes(request, pk):
    """
    renders a partial containing the quotes of a certain book, along with the associated tags
    """
    user = request.user
    book = get_object_or_404(Book, pk=pk)
    quotes = Quote.objects.filter(review__user=user, review__book=book).order_by('-favorite', 'id').prefetch_related(
        Prefetch(
            'quotequotetags',
            queryset=QuoteQuoteTag.objects.select_related('tag_id')
        )
    )

    context = {'quotes': quotes}
    return render(request, "partials/books/book_detail/quotes.html", context)


def remove_book(request, review_id):
    """
    deletes the selected review instance of the book and its associated models
    """
    review = get_object_or_404(Review, id=review_id)
    review.delete()

    return redirect('book_list')


def favorite_quote(request, quote_id):
    """
    mark a quote from book detail page as favorite
    """
    try:
        quote = get_object_or_404(Quote, id=quote_id)
        quote.favorite = not quote.favorite
        quote.save()
        return HttpResponse("""<div class="success-message fade-out">Updated</div>""")
    except:
        return HttpResponse("""<div class="error-message fade-out">Could not update</div>""")


def delete_quote(request, quote_id):
    """
    delete a quote from book detail page
    """
    try:
        quote = get_object_or_404(Quote, id=quote_id)
        quote.delete()
        return HttpResponse("")
    except:
        return HttpResponse("A problem occurred")


def edit_quote(request, quote_id):
    """
    renders a form where you can edit a selected quote
    """
    quote = get_object_or_404(Quote, id=quote_id)
    tags = QuoteTag.objects.filter(quotequotetag__quote_id=quote)

    context = {'quote': quote, 'tags': tags}
    return render(request, 'partials/books/book_detail/edit_quote_overlay.html', context)


def save_edited_quote(request, quote_id):
    """
    updates the selected quote with data from the quote edit overlay
    """
    if request.method == "POST":
        quote = get_object_or_404(Quote, id=quote_id)

        quote_text = request.POST.get("quote-text", "")
        tags_json = request.POST.get("tags", '[]')
        quote_date = request.POST.get("quote-date", None)
        quote_page = request.POST.get("quote-page", None)

        quote.text = quote_text

        if quote_date:
            quote.date_added = quote_date
        else:
            quote.date_added = None

        if quote_page:
            quote.page = quote_page
        else:
            quote.page = None

        try:
            tags_data = json.loads(tags_json) if tags_json else []
        except json.JSONDecodeError:
            return HttpResponse("Invalid tags format", status=400)

        current_tags = set(quote.quotequotetags.values_list('tag_id__name', flat=True))

        tag_names = {tag['value'].strip() for tag in tags_data if 'value' in tag}

        tags_to_add = tag_names - current_tags
        tags_to_remove = current_tags - tag_names

        for tag_name in tags_to_add:
            quote_tag, created = QuoteTag.objects.get_or_create(name=tag_name)
            QuoteQuoteTag.objects.create(quote_id=quote, tag_id=quote_tag)

        for tag_name in tags_to_remove:
            quote_tag = QuoteTag.objects.get(name=tag_name)
            QuoteQuoteTag.objects.filter(quote_id=quote, tag_id=quote_tag).delete()

        quote.save()

        quotes = Quote.objects.filter(id=quote.id).order_by('-favorite', 'id').prefetch_related(
            Prefetch(
                'quotequotetags',
                queryset=QuoteQuoteTag.objects.select_related('tag_id')
            )
        )

        context = {'quotes': quotes}
        return render(request, "partials/books/book_detail/quotes.html", context)


def new_quote_form(request, review_id):
    """
    renders a form where you can add a new quote/note to a book
    """
    context = {"review_id": review_id}
    return render(request, "partials/books/book_detail/new_quote_overlay.html", context)


def save_new_quote(request, review_id):
    """
    saves a new quote with data from the add quote overlay for the selected book
    """
    if request.method == "POST":

        review = get_object_or_404(Review, pk=review_id)

        quote_text = request.POST.get("quote-text", "")
        tags_json = request.POST.get("tags", '[]')
        quote_date = request.POST.get("quote-date", None)
        quote_page = request.POST.get("quote-page", None)

        if not quote_text.strip():
            return HttpResponse("Quote text is required", status=400)

        try:
            tags_data = json.loads(tags_json) if tags_json else []
        except json.JSONDecodeError:
            return HttpResponse("Invalid tags format", status=400)

        quote = Quote.objects.create(
            review=review,
            text=quote_text,
            date_added=quote_date or None,
            page=quote_page or None
        )

        tag_names = {tag['value'].strip() for tag in tags_data if 'value' in tag}
        for tag_name in tag_names:
            quote_tag, _ = QuoteTag.objects.get_or_create(name=tag_name)
            QuoteQuoteTag.objects.create(quote_id=quote, tag_id=quote_tag)

        quotes = Quote.objects.filter(id=quote.id).order_by('-favorite', 'id').prefetch_related(
            Prefetch(
                'quotequotetags',
                queryset=QuoteQuoteTag.objects.select_related('tag_id')
            )
        )

        context = {'quotes': quotes}
        return render(request, "partials/books/book_detail/quotes.html", context)
    return HttpResponse("Bad request")


def update_quote_count(request, review_id):
    """
    updates the button with the quotes count, triggered by htmx when a quote is added/deleted
    """
    review = get_object_or_404(Review, pk=review_id)
    book = review.book
    quotes_number = Quote.objects.filter(review=review).count()
    context = {"book": book, "quotes_no": quotes_number}

    return render(request, "partials/books/book_detail/quotes_count_btn.html", context)


def review_form(request, review_id):
    """
    renders a form to add/edit review
    """
    review = get_object_or_404(Review, pk=review_id)
    context = {'review': review}

    return render(request, "partials/books/book_detail/review_form_overlay.html", context)


def save_review(request, review_id):
    """
    save/update the existing review
    """
    if request.method == "POST":
        review = get_object_or_404(Review, id=review_id)

        review_text = request.POST.get("review-text", "")
        review.review_content = review_text
        review.save()
        context = {'review': review}
        return render(request, "partials/books/book_detail/review_content.html", context)

    return HttpResponse("Bad request")


def delete_book_quotes(request, review_id):
    """
    deletes all quotes associated with a review, also setting the scraped_quotes to false and refreshing the page
    """
    if request.method == "POST":
        review = get_object_or_404(Review, id=review_id)
        Quote.objects.filter(review=review).delete()
        review.scraped_quotes = False
        review.save()
        book_id = review.book.goodreads_id

        return redirect('book_detail', pk=book_id)

    return HttpResponse("Bad request")


def get_monthly_stats(user):
    data = (
        Review.objects.filter(
            user=user,
            bookshelves='read',
            date_read__isnull=False
        )
        .annotate(month=ExtractMonth('date_read'))
        .values('month')
        .annotate(
            books=Count('book_id'),
            pages=Sum('book__number_of_pages'),
            rating=Avg('rating'),
        )
        .order_by('month')
    )

    return list(data)


def get_pub_stats(user):
    results = (
        Review.objects
        .filter(
            user=user,
            bookshelves='read',
            date_read__isnull=False,
            original_publication_year__isnull=False
        )
        .annotate(
            book_title=F('book__title'),
            year_read=ExtractYear('date_read'),
            date_str=Cast('date_read', CharField())
        )
        .values_list('book_title', 'year_read', 'date_str', 'original_publication_year')
    )
    return list(results)


def get_yearly_stats(user):
    reviews = (
        Review.objects
        .filter(
            user=user,
            bookshelves='read',
            book__number_of_pages__isnull=False
        )
        .annotate(
            year_read=Coalesce(
                Cast(ExtractYear('date_read'), CharField()),
                Value('missing date')
            )
        )
        .values('year_read')
        .annotate(
            books=Count('book__title', distinct=True),
            pages=Sum('book__number_of_pages')
        )
        .order_by('-year_read')
    )

    return [(r['year_read'], r['books'], r['pages']) for r in reviews]


def get_genres_stats(user):
    top_genres = (
        Genre.objects
        .exclude(name__in=['Fiction', 'Nonfiction', 'School', 'Audiobook'])
        .filter(
            bookgenre__goodreads_id__review__user=user,
            bookgenre__goodreads_id__review__bookshelves='read'
        )
        .annotate(total=Count('bookgenre__goodreads_id__review', distinct=True))
        .order_by('-total')[:15]
        .values_list('name', 'total')
    )

    return list(top_genres)


def get_genres_stats_by_year(user):
    qs = (
        Genre.objects
        .exclude(name__in=['Fiction', 'Nonfiction', 'School', 'Audiobook'])
        .filter(
            bookgenre__goodreads_id__review__user=user,
            bookgenre__goodreads_id__review__bookshelves='read'
        )
        .annotate(
            year=Coalesce(
                Cast(ExtractYear('bookgenre__goodreads_id__review__date_read'), CharField()),
                Value('missing date')
            )
        )
        .values('name', 'year')
        .annotate(total=Count('bookgenre__goodreads_id__review', distinct=True))
        .order_by('year', '-total')
    )

    top_genres_per_year = defaultdict(list)
    for entry in qs:
        year = entry['year']
        if len(top_genres_per_year[year]) < 10:
            top_genres_per_year[year].append({
                'name': entry['name'],
                'total': entry['total'],
                'year': year
            })

    result = []
    for year, genres in top_genres_per_year.items():
        result.extend(genres)

    return result


def get_genres_cat(user):
    top_categories = (
        Genre.objects
        .filter(
            name__in=['Fiction', 'Nonfiction'],
            bookgenre__goodreads_id__review__user=user,
            bookgenre__goodreads_id__review__bookshelves='read'
        )
        .annotate(total=Count('bookgenre__goodreads_id__review', distinct=True))
        .order_by('-total')
        .values_list('name', 'total')
    )

    return list(top_categories)


def get_author_stats(user):
    data = (
        Review.objects
        .filter(
            user=user,
            bookshelves='read',
            book__number_of_pages__isnull=False
        )
        .values('author')
        .annotate(
            books=Count('author', distinct=True),
            pages=Sum('book__number_of_pages')
        )
        .filter(pages__gt=0)
        .order_by('-pages')[:20]
    )

    return list(data)


def get_author_awards(user):
    data = (
        Review.objects
        .filter(
            user=user,
            bookshelves='read',
            book__award__isnull=False
        )
        .annotate(
            book_title=F('book__title'),
            awards_count=Count('book__award', distinct=True),
            book_goodreads_id=F('book__goodreads_id')
        )
        .values('author', 'book_title', 'awards_count', 'book_goodreads_id')
    )

    return list(data)


def get_author_awards_count(user):
    count = (
        Review.objects
        .filter(
            user=user,
            bookshelves='read',
            book__award__isnull=False
        )
        .values('author')
        .distinct()
        .count()
    )
    return count


def get_awards_data(request, book_id):
    """
    ajax endpoint triggered by the awards chart
    """
    awards = list(Award.objects.filter(goodreads_id_id=book_id).values('name', 'awarded_at'))

    return JsonResponse({'awards': awards})


def get_books_popularity(user):
    data = (
        Review.objects
        .filter(
            user=user,
            bookshelves='read'
        )
        .annotate(
            book_title=F('book__title'),
            ratings_count=F('book__ratings_count'),
            book_goodreads_id=F('book__goodreads_id')
        )
        .values('author', 'book_title', 'ratings_count', 'book_goodreads_id')
        .distinct()
    )

    return list(data)


def get_total_pages_count(user):
    total_pages = (
        Review.objects
        .filter(
            user=user,
            bookshelves='read',
            book__number_of_pages__isnull=False
        )
        .aggregate(total_pages=Sum('book__number_of_pages'))
    )['total_pages'] or 0

    return total_pages


@login_required()
def book_stats(request):
    """
    function used to retrieve data about books using the queries above
    renders different statistics in one page
    """
    user = request.user
    monthly_data = get_monthly_stats(user)
    pub_stats = get_pub_stats(user)
    yearly_stats = get_yearly_stats(user)
    genre_stats = get_genres_stats(user)
    genre_stats_year = get_genres_stats_by_year(user)
    genre_category = get_genres_cat(user)
    author_pages = get_author_stats(user)
    awards = get_author_awards(user)
    awards_count = get_author_awards_count(user)
    ratings = get_books_popularity(user)
    pages_number = get_total_pages_count(user)

    context = {'monthly_data': monthly_data, 'pubStats': pub_stats, 'yearStats': yearly_stats, 'genreStats': genre_stats,
               'genreStatsYear': genre_stats_year, 'genreCategory': genre_category, 'author_pages': author_pages,
               'awards': awards, 'awards_count': awards_count, 'ratings': ratings, 'pages': pages_number}

    return render(request, "stats/book_stats.html", context)


def get_book_locations(user):
    results = (
        Book.objects.filter(
            review__user=user,
            review__bookshelves__in=['read', 'to-read'],
            booklocation__location_id__updated=True
        )
        .values(
            'title',
            status=F('review__bookshelves'),
            year=F('review__original_publication_year'),
            location_name=F('booklocation__location_id__name'),
            country_code=F('booklocation__location_id__code'),
            latitude=F('booklocation__location_id__latitude'),
            longitude=F('booklocation__location_id__longitude')
        )
        .distinct()
    )
    return results


def get_book_locations_stats(user):
    results = (
        Location.objects.filter(
            updated=True,
            booklocation__goodreads_id__review__user=user,
            booklocation__goodreads_id__review__bookshelves__in=['read', 'to-read']
        )
        .values('name')
        .annotate(places_count=Count('booklocation__goodreads_id', distinct=True))
        .order_by('-places_count')[:15]
    )

    return results


def update_location(location, location_data):
    if location_data:
        try:
            country_code = location_data.code
            location.code = country_code
            location.latitude = location_data.latitude
            location.longitude = location_data.longitude
            location.updated = True
            location.requested = True
            location.save()
        except:
            location.latitude = location_data.latitude
            location.longitude = location_data.longitude
            location.updated = True
            location.requested = True
            location.save()


def get_local_locations_data(request):
    """
    function that attempts to get location coordinates from local database to reduce the use of geocoding services
    for already popular locations
    it looks for location data in place -> country -> region -> region, country -> city -> city, region -> city, country
    """
    user = request.user
    queryset = Location.objects.filter(requested=False, booklocation__goodreads_id__review__user=user).distinct()

    if queryset:
        for location in queryset:

            try:
                location_data = Place.objects.get(name=location)
                update_location(location, location_data)
            except Place.DoesNotExist:
                try:
                    location_data = Country.objects.get(name=location)
                    update_location(location, location_data)
                except Country.DoesNotExist:
                    try:
                        location_data = Region.objects.get(Q(region_name=location) | Q(combined_name=location))
                        update_location(location, location_data)
                    except Region.DoesNotExist:
                        try:
                            location_data = City.objects.filter(city_name=location).order_by('-population').first()
                            update_location(location, location_data)
                        except City.DoesNotExist:
                            try:
                                location_data = City.objects.filter(city_name_ascii=location).order_by('-population').first()
                                update_location(location, location_data)
                            except City.DoesNotExist:
                                continue

    queryset_adv = Location.objects.filter(requested=False, booklocation__goodreads_id__review__user=user).distinct()

    if queryset_adv:
        for location in queryset_adv:

            try:
                location_query = City.objects.annotate(city_region=Concat('city_name', Value(', '), 'admin_name'))
                location_data = location_query.get(city_region=location)
                update_location(location, location_data)
            except City.DoesNotExist:
                try:
                    location_query = City.objects.annotate(city_region=Concat('city_name', Value(', '), 'country'))
                    location_data = location_query.get(city_region=location)
                    update_location(location, location_data)
                except City.DoesNotExist:
                    location.requested = True
                    location.save()

    return redirect('book_map')


@login_required()
def book_world_page(request):

    """
    queries the db for locations which lack geocoding data (requested = false)
    if empty, set value to 0 and hide Get location data info in js file
    """

    user = request.user
    queryset = Location.objects.filter(requested=False, booklocation__goodreads_id__review__user=user).distinct()
    empty_loc = len(queryset) or 0
    location_stats = get_book_locations_stats(user)

    locations_data = get_book_locations(user)

    context = {'emptyLoc': empty_loc, 'queryset': queryset, 'locations': list(locations_data),
               'locations_stats': location_stats
               }

    return render(request, "books/book_map.html", context)


@login_required()
def wordcloud_filter(request):
    """
    renders the genres filter for the wordcloud page
    """
    user = request.user
    excluded_genres = ['Fiction', 'School', 'Audiobook', 'Nonfiction']

    genres = (
        Genre.objects
        .exclude(name__in=excluded_genres)
        .filter(
            bookgenre__goodreads_id__language='English',
            bookgenre__goodreads_id__review__user=user,
            bookgenre__goodreads_id__review__bookshelves='read'
        )
        .annotate(total=Count('bookgenre'))
        .order_by('-total')
        .values_list('name', 'total')[:30]
    )

    context = {'genres': genres}

    return render(request, "books/wordcloud_filter.html", context)


def get_book_description_by_genre(language, genre, user):
    descriptions = (
        Book.objects.filter(
            language=language,
            bookgenre__genre_id__name=genre,
            review__user=user,
            review__bookshelves='read'
        )
        .values_list('description', flat=True)
        .distinct()
    )

    return descriptions


@login_required()
def generate_word_cloud(request):
    """
    returns a word frequency count for the descriptions of books from the requested genre and English language.
    will be used with the wordcloud2.js library
    """
    language = request.GET.get('language', 'English')
    genre = request.GET.get('genre', 'Fiction')
    user = request.user

    book_descriptions = (
        Book.objects.filter(
            language=language,
            bookgenre__genre_id__name=genre,
            review__user=user,
            review__bookshelves='read'
        )
        .values_list('description', flat=True)
        .distinct()
    )

    nlp = spacy.load("en_core_web_sm")
    stop_words = nlp.Defaults.stop_words
    additional_stopwords = {"year", "novel", "--The", "ISBN"}
    stop_words |= additional_stopwords

    word_freqs = Counter()
    for desc in book_descriptions:
        cleaned_description = unescape(desc)
        if not cleaned_description.strip():
            continue

        doc = nlp(cleaned_description)
        tokens = [token.lemma_ for token in doc if token.lemma_.lower() not in stop_words and len(token.text) >= 4 and token.pos_ in {"NOUN", "PROPN", "ADJ", "VERB"}]
        word_freqs.update(tokens)

        sorted_word_freqs = dict(sorted(word_freqs.items(), key=lambda x: x[1], reverse=True)[:100])

    context = {'word_freqs': sorted_word_freqs}

    return render(request, "books/book_word_cloud.html", context)


def get_author_locations(user):
    data = (
        AuthLoc.objects
        .filter(
            authorlocation_id__updated=True,
            author_id__book__review__user=user
        )
        .values(
            author_name=F('author_id__name'),
            place=F('authorlocation_id__name'),
            code=F('authorlocation_id__code'),
            latitude=F('authorlocation_id__latitude'),
            longitude=F('authorlocation_id__longitude')
        )
        .distinct()
    )
    return list(data)


def get_author_locations_stats(user):
    results = (
        AuthorLocation.objects
        .filter(
            updated=True,
            authloc__author_id__book__review__user=user
        )
        .annotate(places_count=Count('authloc', distinct=True))
        .values('name', 'places_count')
        .order_by('-places_count')[:15]
    )
    return results


def update_author_location(location, location_data):
    if location_data:
        try:
            country_code = location_data.code
            location.code = country_code
            location.latitude = location_data.latitude
            location.longitude = location_data.longitude
            location.updated = True
            location.save()
        except:
            location.latitude = location_data.latitude
            location.longitude = location_data.longitude
            location.updated = True
            location.save()


class AuthorMapView(LoginRequiredMixin, View):
    """
    extract NER data from author's description
    I haven't found a good use for other ner entities yet
    """
    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Author.objects.filter(processed_ner=False, book__review__user=request.user).distinct()
        empty_loc = len(queryset) or 0
        location_stats = get_author_locations_stats(user)

        locations_data = get_author_locations(user)

        context = {'emptyLoc': empty_loc, 'queryset': queryset, 'locations': locations_data,
                   'locations_stats': location_stats}

        return render(request, "authors/author_map.html", context)

    def post(self, request, *args, **kwargs):
        queryset = Author.objects.filter(processed_ner=False, book__review__user=request.user).distinct()

        if queryset:
            nlp = spacy.load("en_core_web_sm")
            for author in queryset:
                if not author.about:
                    author.processed_ner = True
                    author.save()

                else:
                    doc = nlp(author.about)

                    # Extract entities and convert to list, after storing only unique values
                    gpe_list = list(set(ent.text.strip() for ent in doc.ents if ent.label_ == "GPE" and all(token.pos_ == "PROPN" for token in ent)))
                    loc_list = list(set(ent.text.strip() for ent in doc.ents if ent.label_ == "LOC"))
                    person_list = list(set(ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON" and all(token.pos_ == "PROPN" for token in ent)))

                    author_ner = AuthorNER.objects.create(
                        author=author,
                        gpe=str(gpe_list),
                        loc=str(loc_list),
                        person=str(person_list)
                    )

                    author_ner.save()
                    # Mark the author as processed
                    author.processed_ner = True
                    author.save()

                    if gpe_list:
                        for location in gpe_list:
                            location_obj, created = AuthorLocation.objects.get_or_create(name=location)
                            try:
                                location_data = Place.objects.get(name=location_obj)
                                update_author_location(location_obj, location_data)
                                author_loc_obj = AuthLoc(author_id=author, authorlocation_id=location_obj)
                                author_loc_obj.save()
                            except Place.DoesNotExist:
                                try:
                                    location_data = Country.objects.get(name=location_obj)
                                    update_author_location(location_obj, location_data)
                                    author_loc_obj = AuthLoc(author_id=author, authorlocation_id=location_obj)
                                    author_loc_obj.save()
                                except Country.DoesNotExist:
                                    try:
                                        location_data = Region.objects.get(Q(region_name=location) | Q(combined_name=location))
                                        update_author_location(location_obj, location_data)
                                        author_loc_obj = AuthLoc(author_id=author, authorlocation_id=location_obj)
                                        author_loc_obj.save()
                                    except Region.DoesNotExist:
                                        try:
                                            location_data = City.objects.filter(city_name=location_obj).order_by(
                                                '-population').first()
                                            update_author_location(location_obj, location_data)
                                            author_loc_obj = AuthLoc(author_id=author, authorlocation_id=location_obj)
                                            author_loc_obj.save()
                                        except City.DoesNotExist:
                                            try:
                                                location_data = City.objects.filter(city_name_ascii=location_obj).order_by(
                                                    '-population').first()
                                                update_author_location(location_obj, location_data)
                                                author_loc_obj = AuthLoc(author_id=author, authorlocation_id=location_obj)
                                                author_loc_obj.save()
                                            except City.DoesNotExist:
                                                continue

        return redirect("author_map")


def get_authors_map_data(request, location):
    """
    function which is triggered by markers and clusters in the author map view
    There is an issue when more locations share the same coordinates (ex: New York and New York City)
    which will cause the author to appear more than once in the list
    """

    user = request.user
    author_location = AuthorLocation.objects.get(name=location)
    latitude = author_location.latitude
    longitude = author_location.longitude
    matching_locations = AuthorLocation.objects.filter(latitude=latitude, longitude=longitude)
    authors = (
        Author.objects.filter(
            authloc__authorlocation_id__in=matching_locations,
            book__review__user=user
        )
        .distinct()
        .values('name')
    )

    return JsonResponse({'authors': list(authors)})


def get_books_map_data(request, location):
    """
    function which is triggered by markers and clusters in the book map view
    It returns books ordered by original publication year and their shelf, which will get sorted in the .js file
    """
    user = request.user
    books_location = Location.objects.get(name=location)
    latitude = books_location.latitude
    longitude = books_location.longitude
    matching_locations = Location.objects.filter(latitude=latitude, longitude=longitude)

    books = (
        Book.objects.filter(
            booklocation__location_id__in=matching_locations,
            review__user=user
        )
        .annotate(
            publication_year=F('review__original_publication_year'),
            shelf=F('review__bookshelves')
        )
        .order_by('publication_year')
        .values('title', 'publication_year', 'shelf')
    )

    return JsonResponse({'books': list(books)})


def book_gallery(request):
    """
    renders the book gallery page and the filters which fill up the sidebars.
    I set up paginators on each one, except the search bar, which returns the first 30 results.
    Each filter returns the books and the context name of the filter which I used in the book_covers partial to
    display the title of the selected filter at a fixed position.
    Additionally, I used the context received to trigger htmx request for paginator.
    """
    year_read = Review.objects.filter(bookshelves='read').annotate(year_read=ExtractYear('date_read')).values('year_read').annotate(num_books=Count('id')).order_by('-year_read')
    shelves = Review.objects.values('bookshelves').annotate(num_books=Count('id')).order_by('-num_books')
    genres_count = Genre.objects.filter(bookgenre__goodreads_id__review__bookshelves__iexact='read').annotate(total=Count('name')).order_by('-total')
    tags_count = UserTag.objects.annotate(total=Count('reviewtag__review')).filter(total__gt=0).order_by('-total', 'name')
    rating_count = Review.objects.filter(bookshelves='read').values('rating').annotate(num_books=Count('id')).order_by('-rating')
    has_review_count = Book.objects.filter(review__bookshelves__iexact='read').exclude(Q(review__review_content__isnull=True) | Q(review__review_content__exact='')).count()
    no_review_count = Book.objects.filter(review__bookshelves__iexact='read').filter(Q(review__review_content__isnull=True) | Q(review__review_content__exact='')).count()

    context = {'shelves': shelves, 'year_read': year_read, 'genres': genres_count, 'tags': tags_count, 'ratings': rating_count,
               'has_review': has_review_count, 'no_review': no_review_count
               }

    return render(request, 'books/book_gallery.html', context)


def gallery_shelf_filter(request):

    shelf = request.GET.get('shelf')
    books_queryset = Book.objects.filter(review__bookshelves__iexact=shelf).order_by('-review__date_added')

    paginator = Paginator(books_queryset, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    context = {'books': books, 'shelf': shelf}

    return render(request, 'partials/books/book_covers.html', context)


def gallery_rating_filter(request):
    rating = request.GET.get('rating')
    books_queryset = Book.objects.filter(review__bookshelves__iexact='read', review__rating=rating).order_by('-review__date_added')

    paginator = Paginator(books_queryset, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    context = {'books': books, 'rating': rating}

    return render(request, 'partials/books/book_covers.html', context)


def gallery_rating_update(request, pk, new_rating):

    try:
        review = get_object_or_404(Review, goodreads_id=pk)
        review.rating = new_rating
        review.save()

        return HttpResponse("""<div class="success-message fade-out">Updated</div>""")

    except:
        return HttpResponse("""<div class="error-message fade-out">Could not update</div>""")


def gallery_delete_review(request, pk):
    """
    delete review from selected book.
    send some visual feedback to the frontend and, after .5 sec re-renders the book overlay.
    """
    if request.method == 'POST':
        review = get_object_or_404(Review, goodreads_id=pk)
        review.review_content = ""
        review.save()
        return HttpResponse("""<div class="success-message fade-out">Deleting...</div>""")
    else:
        return HttpResponse("""<div class="error-message fade-out">Not deleted</div>""")


def gallery_add_review(request, pk):
    """
    add review to the selected book.
    send some visual feedback to the frontend and, after .5 sec re-renders the book overlay.
    """
    if request.method == 'POST':
        review_content = request.POST.get('review')
        review = get_object_or_404(Review, goodreads_id=pk)
        review.review_content = review_content
        review.save()
        return HttpResponse("""<div class="success-message fade-out">Saving...</div>""")
    else:
        return HttpResponse("""<div class="error-message fade-out">Not saved</div>""")


def gallery_review_sidebar_update(request):
    """
    updates the review filter on the left sidebar when a book receives a review change. (add/delete)
    """
    has_review_count = Book.objects.filter(review__bookshelves__iexact='read').exclude(Q(review__review_content__isnull=True) | Q(review__review_content__exact='')).count()

    no_review_count = Book.objects.filter(review__bookshelves__iexact='read').filter(Q(review__review_content__isnull=True) | Q(review__review_content__exact='')).count()
    context = {'has_review': has_review_count, 'no_review': no_review_count}

    return render(request, 'partials/books/gallery_reviews_filter.html', context)


def gallery_rating_sidebar_update(request):
    """
    updates the rating filter on the left sidebar when a book has a rating update
    """
    rating_count = Review.objects.filter(bookshelves='read').values('rating').annotate(num_books=Count('id')).order_by('-rating')
    context = {'ratings': rating_count}

    return render(request, 'partials/books/gallery_ratings.html', context)


def gallery_review_filter(request):
    has_review = request.GET.get('review')
    if has_review.lower() == 'true':
        books_queryset = Book.objects.filter(review__bookshelves__iexact='read').exclude(Q(review__review_content__isnull=True) | Q(review__review_content__exact='')).order_by('-review__date_added')
    elif has_review.lower() == 'false':
        books_queryset = Book.objects.filter(review__bookshelves__iexact='read').filter(Q(review__review_content__isnull=True) | Q(review__review_content__exact='')).order_by('-review__date_added')

    paginator = Paginator(books_queryset, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    context = {'books': books, 'review': has_review}

    return render(request, 'partials/books/book_covers.html', context)


def gallery_year_filter(request):
    year = request.GET.get('year')
    if int(year) > 1:
        books_queryset = Book.objects.filter(review__bookshelves__iexact='read', review__date_read__year=year).order_by('-review__date_added')
    else:
        books_queryset = Book.objects.filter(review__bookshelves__iexact='read').filter(review__date_read__year__isnull=True).order_by('-review__date_added')

    paginator = Paginator(books_queryset, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    context = {'books': books, 'year': year}

    return render(request, 'partials/books/book_covers.html', context)


def gallery_genre_filter(request):
    """
    returns books containing the selected tag or genre.
    I've considered updating the genre sidebar each time a filter on the left gets selected, but I think it would
    be TOO distracting
    """
    genre = request.GET.get('genre')
    books_queryset = Book.objects.filter(review__bookshelves__iexact='read', bookgenre__genre_id__name__iexact=genre).order_by('-review__date_added')

    paginator = Paginator(books_queryset, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    context = {'books': books, 'genre': genre}

    return render(request, 'partials/books/book_covers.html', context)


def gallery_tag_filter(request):
    """
    returns books containing the selected tag
    """
    tag = request.GET.get('tag')
    books_queryset = Book.objects.filter(review__reviewtag__tag__name__iexact=tag).order_by('-review__date_added')

    paginator = Paginator(books_queryset, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    context = {'books': books, 'tag': tag}

    return render(request, 'partials/books/book_covers.html', context)


def gallery_author_filter(request):
    contributor = request.GET.get('contributor')
    books_queryset = Book.objects.filter(author__icontains=contributor).order_by('-review__date_added')

    paginator = Paginator(books_queryset, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    context = {'books': books, 'contributor': contributor}

    return render(request, 'partials/books/book_covers.html', context)


def clear_book_filter(request):
    """
    simply renders a blank page, book_cover with no books
    """
    return render(request, 'partials/books/book_covers.html')


def gallery_tag_sidebar_update(request):
    """
    updates the tags filter on the right sidebar
    """
    tags = UserTag.objects.annotate(total=Count('reviewtag__review')).filter(total__gt=0).order_by('-total', 'name')
    context = {'tags': tags}

    return render(request, 'partials/books/gallery_tags.html', context)


def gallery_tag_update(request, pk):
    """
    updates the list of tags of a book
    triggered by htmx when the text input changes
    there's a neat interaction with tagify.js which changes the input only when a tag is submitted or removed; + filters
    """
    book = Book.objects.get(pk=pk)
    review = Review.objects.get(goodreads_id=book)
    tags_json = request.POST.get('tags', '[]')

    try:
        tags_data = json.loads(tags_json) if tags_json else []
    except json.JSONDecodeError:
        return HttpResponse("Invalid tags format", status=400)

    current_tags = set(review.reviewtag_set.values_list('tag__name', flat=True))

    tag_names = {tag['value'].strip() for tag in tags_data if 'value' in tag}

    tags_to_add = tag_names - current_tags
    tags_to_remove = current_tags - tag_names

    for tag_name in tags_to_add:
        user_tag, created = UserTag.objects.get_or_create(name=tag_name)
        ReviewTag.objects.create(review=review, tag=user_tag)

    for tag_name in tags_to_remove:
        user_tag = UserTag.objects.get(name=tag_name)
        ReviewTag.objects.filter(review__goodreads_id=book, tag=user_tag).delete()

    return HttpResponse("ok")


def gallery_year_sidebar_update(request):
    year_read = Review.objects.filter(bookshelves='read').annotate(year_read=ExtractYear('date_read')).values('year_read').annotate(num_books=Count('id')).order_by('-year_read')
    context = {'year_read': year_read}

    return render(request, 'partials/books/gallery_years_filter.html', context)


def gallery_date_read_update(request, pk):
    """
    updates the date read and returns a partial containing said date in book overlay
    """
    if request.method == "POST":
        date_read = request.POST.get("date")
        book = Book.objects.get(pk=pk)
        review = Review.objects.get(goodreads_id=pk)
        review.date_read = date_read if date_read else None
        review.save()

        review = book.review_set.first()

        context = {'book': book, 'review': review}

        return render(request, 'partials/books/date_read_display.html', context)

    return JsonResponse({"error": "Invalid request."}, status=400)


def gallery_shelf_update(request, pk):
    if request.method == "POST":
        shelf = request.POST.get("bookshelf")
        review = Review.objects.get(goodreads_id=pk)
        if shelf:
            if shelf == "add-new":
                context = {'pk': pk}
                return render(request, 'partials/books/gallery_add_new_shelf.html', context)

            review.bookshelves = shelf
            review.save()

            shelves = Review.objects.values('bookshelves').annotate(num_books=Count('id')).order_by('-num_books')
            context = {'review': review, 'gallery_shelves': shelves}
            return render(request, 'partials/books/gallery_shelf_select.html', context)

    return JsonResponse({"error": "Invalid request."}, status=400)


def gallery_shelf_sidebar_update(request):
    shelves = Review.objects.values('bookshelves').annotate(num_books=Count('id')).order_by('-num_books')
    context = {'shelves': shelves}

    return render(request, 'partials/books/gallery_shelves.html', context)


def gallery_overlay(request, pk):
    """
    renders the overlay containing the book's info.
    I had to render the rating radio buttons in the opposite order to work with the frontend, but it doesn't alter
    the functionality.
    """
    book = get_object_or_404(Book, pk=pk)
    rating_range = range(5, 0, -1)
    tags = UserTag.objects.filter(reviewtag__review__goodreads_id=book)
    genres = Genre.objects.filter(bookgenre__goodreads_id=book)
    shelves = Review.objects.values('bookshelves').annotate(num_books=Count('id')).order_by('-num_books')

    context = {'book': book, 'tags': tags, 'genres': genres, 'rating_range': rating_range,
               'gallery_shelves': shelves}

    return render(request, 'partials/books/gallery_overlay.html',  context)


def search_book(request):
    """
    live search bar, triggered by htmx at 3 characters typed
    """
    search_text = request.POST.get('search')
    books = Book.objects.filter(
        (Q(title__icontains=search_text) | Q(author__icontains=search_text)) & Q(review__isnull=False)).order_by('-review__date_added')[:30]

    context = {'books': books, "search_text": search_text}
    return render(request, 'partials/books/book_covers.html', context)


def export_quotes_csv(request):
    """
    creates a csv file containing quotes data
    """
    books_with_quotes = (Book.objects.filter(review__bookshelves__iexact='read', quote__isnull=False).distinct(
                         ).prefetch_related(
        Prefetch(
            'review_set',
            queryset=Review.objects.filter(bookshelves__iexact='read')
        )
    ))

    queryset = Quote.objects.filter(book__in=books_with_quotes).select_related('book').prefetch_related(
        Prefetch(
            'quotequotetags',
            queryset=QuoteQuoteTag.objects.select_related('tag_id')
        )
    )

    data = []

    for quote in queryset:
        tags = ", ".join(qqt.tag_id.name for qqt in quote.quotequotetags.all())

        author_r = None
        if quote.book.review_set.exists():
            author_r = quote.book.review_set.first().author

        data.append({
            'Book Id': quote.book.goodreads_id,
            'Title': quote.book,
            'Author': author_r,
            'Page': quote.page,
            'Date Added': quote.date_added.strftime('%Y/%m/%d') if quote.date_added else None,
            'Favorite': quote.favorite or None,
            'Tags': tags,
            'Content': quote.text,
            'Quotes Url': quote.book.quotes_url
        })
    df = pd.DataFrame(data)

    csv_buffer = df.to_csv(index=False).encode('utf-8')

    response = HttpResponse(csv_buffer, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="quotes.csv"'
    return response


@login_required()
def quotes_page(request):
    """
    renders the main page of quotes
    I tried adding paginators, but it messes the masonry.js layout
    """
    user = request.user
    tags = (
        QuoteTag.objects.annotate(
            total=Count(
                'quotequotetag__quote_id',  # follow the ForeignKey to Quote
                filter=Q(quotequotetag__quote_id__review__user=user),  # only current user's quotes
                distinct=True
            )
        )
        .filter(total__gt=0)
        .order_by('-total', 'name')
    )

    no_tags_count = Quote.objects.filter(review__user=user).annotate(
        tag_count=Count('quotequotetags')
    ).filter(tag_count=0).count()

    fav_count = Quote.objects.filter(favorite=True, review__user=user).count()

    books = (
        Book.objects.annotate(
            num_quotes=Count('review__quotes', filter=Q(review__user=user), distinct=True)
        )
        .filter(num_quotes__gt=0)
        .order_by('title')
    )

    context = {'tags': tags, 'no_tags_count': no_tags_count, 'fav_count': fav_count, 'books': books}

    return render(request, 'books/quotes.html', context)


def quotes_tag_filter(request):
    """
    returns quotes containing the selected tag and handles the case with quotes with no tags
    """
    user = request.user
    tag = request.GET.get('tag')
    quotes = None
    if tag == "no_tag":
        quotes = (
            Quote.objects
            .filter(review__user=user)
            .annotate(tag_count=Count('quotequotetags'))
            .filter(tag_count=0)
            .select_related('review__book')
        )
        tag_name = "No Tags"
    else:
        tag_name = get_object_or_404(QuoteTag, name=tag)
        quotes = (
            Quote.objects
            .filter(review__user=user)
            .filter(quotequotetags__tag_id=tag_name)
            .select_related('review__book')
        )

    context = {'quotes': quotes, 'tag': tag_name}
    return render(request, 'partials/books/quotes/quotes.html', context)


def quotes_favorite_filter(request):
    """
    returns favorite quotes
    """
    user = request.user
    quotes = Quote.objects.filter(favorite=True, review__user=user)
    context = {'quotes': quotes, 'fav_title': "Favorite quotes"}

    return render(request, 'partials/books/quotes/quotes.html', context)


def quotes_book_filter(request, book_id):
    """
    returns quotes from the selected book
    """
    user = request.user
    book = get_object_or_404(Book.objects.prefetch_related('review_set__quotes'), goodreads_id=book_id)
    quotes = (
        Quote.objects
        .filter(review__book=book, review__user=user)
        .order_by('-favorite', 'id')
    )

    context = {'quotes': quotes, 'book_title': book.title}

    return render(request, 'partials/books/quotes/quotes.html', context)


def quotes_update_fav_sidebar(request):
    """
    updates the favorites count in the left sidebar
    """
    user = request.user
    fav_count = Quote.objects.filter(favorite=True, review__user=user).count()
    context = {'fav_count': fav_count}

    return render(request, 'partials/books/quotes/fav_quotes_sidebar.html', context)


def quotes_update_books_sidebar(request):
    """
    updates the book list in the left sidebar
    """
    user = request.user
    books = (
        Book.objects.annotate(
            num_quotes=Count('review__quotes', filter=Q(review__user=user), distinct=True)
        )
        .filter(num_quotes__gt=0)
        .order_by('title')
    )
    context = {'books': books}

    return render(request, 'partials/books/quotes/book_list_sidebar.html', context)


def quotes_update_tags_sidebar(request):
    """
    updates the tags count in the right sidebar
    """
    user = request.user
    tags = (
        QuoteTag.objects.annotate(
            total=Count(
                'quotequotetag__quote_id',
                filter=Q(quotequotetag__quote_id__review__user=user),
                distinct=True
            )
        )
        .filter(total__gt=0)
        .order_by('-total', 'name')
    )

    no_tags_count = (
        Quote.objects.filter(review__user=user)
        .annotate(tag_count=Count('quotequotetags'))
        .filter(tag_count=0)
        .count()
    )

    context = {'tags': tags, 'no_tags_count': no_tags_count}

    return render(request, 'partials/books/quotes/quotes_tags.html', context)


def highlight_search_term(text, search_term):
    if search_term:
        lower_text = text.lower()
        lower_search_term = search_term.lower()

        start = 0
        result = []

        while (index := lower_text.find(lower_search_term, start)) != -1:
            # Append text before the match
            result.append(escape(text[start:index]))
            # Append the highlighted match
            result.append(f"<mark>{escape(text[index:index + len(search_term)])}</mark>")
            # Move the start pointer
            start = index + len(search_term)

        # Append any remaining text
        result.append(escape(text[start:]))

        return ''.join(result)

    return escape(text)


def quotes_page_search(request):
    """
    returns quotes containing the searched term, adding <mark> tags to highlight it
    """
    user = request.user
    search_text = request.GET.get('search')
    quotes = Quote.objects.filter(text__icontains=search_text, review__user=user)
    results_no = quotes.count()

    for quote in quotes:
        quote.text = highlight_search_term(quote.text, search_text)

    context = {'quotes': quotes, "search_text": search_text, 'results_no': results_no}
    return render(request, 'partials/books/quotes/quotes.html', context)
