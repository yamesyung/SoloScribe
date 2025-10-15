import re
import os
import ast
import json
import spacy
import pandas as pd
from collections import Counter
from csv import DictReader
from io import TextIOWrapper
from html import unescape
from datetime import datetime

from django.conf import settings
from django.urls import reverse
from django.utils.html import escape
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, View
from django.db.models import Q, Value, Count, F, Prefetch
from django.db.models.functions import Concat, ExtractYear
from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
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


def get_book_detail(pk):
    with connection.cursor() as cursor:
        query = """
                select ba.author_id, br.id, br.author, br.rating, br.bookshelves, TO_CHAR(br.date_read, 'dd-mm-yyyy'),
                br.original_publication_year, br.review_content from books_author ba, books_review br
                where LOWER(REGEXP_REPLACE(br.author, '\s+', ' ', 'g')) = LOWER(REGEXP_REPLACE(ba."name", '\s+', ' ', 'g'))
                and br.goodreads_id_id =  %s
        """
        cursor.execute(query, [pk])
        result = cursor.fetchone()

        return result


@login_required()
def book_detail(request, pk):
    """
    function used to display book detail page.
    It uses the book model and the above query
    """
    author_data = get_book_detail(pk)
    review = get_object_or_404(Review, goodreads_id=pk)
    book = get_object_or_404(Book, pk=pk)
    quotes_number = Quote.objects.filter(book=book).count()
    rating_range = range(5, 0, -1)

    genres = Genre.objects.filter(bookgenre__goodreads_id=book)
    tags = UserTag.objects.filter(reviewtag__review__goodreads_id=book)
    places = Location.objects.filter(booklocation__goodreads_id=book)

    shelves = Review.objects.values('bookshelves').annotate(num_books=Count('id')).order_by('-num_books')

    context = {'author_data': author_data, 'book': book, 'review': review, 'quotes_no': quotes_number,
               'rating_range': rating_range, 'gallery_shelves': shelves,
               'genres': genres, 'tags': tags, 'places': places}

    return render(request, "books/book_detail.html", context)


def edit_book_form(request, pk):
    book = get_object_or_404(Book, pk=pk)
    review = get_object_or_404(Review, goodreads_id=pk)
    genres = Genre.objects.filter(bookgenre__goodreads_id=book)
    tags = UserTag.objects.filter(reviewtag__review__goodreads_id=book)

    context = {'book': book, 'review': review, 'genres': genres, 'tags': tags}

    return render(request, 'partials/books/book_detail/edit_book_form.html', context)


def save_book_edit(request, pk):
    if request.method == "POST":
        book = get_object_or_404(Book, goodreads_id=pk)
        review = Review.objects.get(goodreads_id=book)

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
                ReviewTag.objects.filter(review__goodreads_id=book, tag=user_tag).delete()
            except Genre.DoesNotExist:
                continue

        return redirect(reverse('book_detail', args=[pk]))
    return redirect(reverse('book_detail', args=[pk]))


def book_detail_quotes(request, pk):
    """
    renders a partial containing the quotes of a certain book, along with the associated tags
    """
    book = get_object_or_404(Book, pk=pk)
    quotes = Quote.objects.filter(book=book).order_by('-favorite', 'id').prefetch_related(
        Prefetch(
            'quotequotetags',
            queryset=QuoteQuoteTag.objects.select_related('tag_id')
        )
    )

    context = {'quotes': quotes}
    return render(request, "partials/books/book_detail/quotes.html", context)


def remove_book(request, pk):
    """
    deletes the selected book and related models from db
    however, the author model stays due to not being related
    it may remain some isolated authors when deleting for now
    """
    book = get_object_or_404(Book, goodreads_id=pk)
    book.delete()

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


def new_quote_form(request, book_id):
    """
    renders a form where you can add a new quote/note to a book
    """
    context = {"book_id": book_id}
    return render(request, "partials/books/book_detail/new_quote_overlay.html", context)


def save_new_quote(request, book_id):
    """
    saves a new quote with data from the add quote overlay for the selected book
    """
    if request.method == "POST":

        book = get_object_or_404(Book, goodreads_id=book_id)

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
            book=book,
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


def update_quote_count(request, book_id):
    """
    updates the button with the quotes count, triggered by htmx when a quote is added/deleted
    """
    book = get_object_or_404(Book, goodreads_id=book_id)
    quotes_number = Quote.objects.filter(book=book).count()
    context = {"book": book, "quotes_no": quotes_number}

    return render(request, "partials/books/book_detail/quotes_count_btn.html", context)


def review_form(request, book_id):
    """
    renders a form to add/edit review
    """
    review = get_object_or_404(Review, id=book_id)
    context = {'review': review}

    return render(request, "partials/books/book_detail/review_form_overlay.html", context)


def save_review(request, book_id):
    """
    save/update the existing review
    """
    if request.method == "POST":
        review = get_object_or_404(Review, id=book_id)

        review_text = request.POST.get("review-text", "")
        review.review_content = review_text
        review.save()
        context = {'review': review}
        return render(request, "partials/books/book_detail/review_content.html", context)

    return HttpResponse("Bad request")


def delete_book_quotes(request, pk):
    """
    deletes all quotes associated with a book, also setting the scraped_quotes to false and refreshing the page
    """
    if request.method == "POST":
        book = get_object_or_404(Book, goodreads_id=pk)
        Quote.objects.filter(book=book).delete()
        book.scraped_quotes = False
        book.save()

        return redirect(reverse('book_detail', args=[pk]))

    return HttpResponse("Bad request")


def get_monthly_stats():
    with connection.cursor() as cursor:
        query = """
                WITH all_months AS (
                    SELECT generate_series(1, 12) AS month
                )
                SELECT 
                    am.month, 
                    COALESCE(COUNT(br.goodreads_id_id), 0) AS books, 
                    COALESCE(SUM(bb.number_of_pages), 0) AS pages,
                    COALESCE(AVG(CASE WHEN br.rating > 0 THEN br.rating END)::numeric(10,2), 0) AS rating
                FROM 
                    all_months am
                LEFT JOIN 
                    books_review br ON EXTRACT('month' FROM br.date_read) = am.month 
                    AND br.bookshelves = 'read' 
                    AND br.date_read IS NOT NULL
                LEFT JOIN 
                    books_book bb ON bb.goodreads_id = br.goodreads_id_id
                GROUP BY 
                    am.month
                ORDER BY 
                    am.month;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_pub_stats():
    with connection.cursor() as cursor:
        query = """
                select bb.title, to_char(br.date_read, 'yyyy') as year_read, 
                to_char(br.date_read, 'yyyy-mm-dd'), br.original_publication_year 
                from books_book bb, books_review br 
                where bb.goodreads_id = br.goodreads_id_id 
                and br.bookshelves = 'read' and br.date_read notnull and br.original_publication_year notnull
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_yearly_stats():
    with connection.cursor() as cursor:
        query = """
                select coalesce(to_char(br.date_read, 'yyyy'), 'missing date') as year_read, 
                count(bb.title) as books, sum(bb.number_of_pages) as pages
                from books_book bb, books_review br 
                where bb.goodreads_id = br.goodreads_id_id and br.bookshelves = 'read' and bb.number_of_pages notnull
                group by year_read
                order by year_read desc
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_genres_stats():
    with connection.cursor() as cursor:
        query = """
                select bg."name", count(bg."name") as total
                from books_genre bg, books_bookgenre bb, books_review br 
                where br.bookshelves = 'read' and bg."name" not in ('Fiction', 'Nonfiction', 'School', 'Audiobook')
                and bg.id = bb.genre_id_id and br.goodreads_id_id = bb.goodreads_id_id 
                group by bg."name" 
                order by total desc
                limit 15
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_genres_stats_by_year():
    with connection.cursor() as cursor:
        query = """
                WITH ranked_genres AS (
                    SELECT
                        bg."name",
                        coalesce(TO_CHAR(br.date_read, 'yyyy'), 'missing date') AS year,
                        COUNT(bg."name") AS total,
                        ROW_NUMBER() OVER (PARTITION BY coalesce(TO_CHAR(br.date_read, 'yyyy'), 'missing date') ORDER BY COUNT(bg."name") DESC) AS rnk
                    FROM
                        books_genre bg
                    JOIN
                        books_bookgenre bb ON bg.id = bb.genre_id_id
                    JOIN
                        books_review br ON br.goodreads_id_id = bb.goodreads_id_id
                    WHERE
                        br.bookshelves = 'read'
                        AND bg."name" NOT IN ('Fiction', 'Nonfiction', 'School', 'Audiobook')
                    GROUP BY
                        bg."name", year
                )
                SELECT
                    "name",
                    total,
                    year
                FROM
                    ranked_genres
                WHERE
                    rnk <= 10;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_genres_cat():
    with connection.cursor() as cursor:
        query = """
                select bg."name", count(bg."name") as total
                from books_genre bg, books_bookgenre bb, books_review br 
                where br.bookshelves = 'read' and bg."name" in ('Fiction', 'Nonfiction')
                and bg.id = bb.genre_id_id and br.goodreads_id_id = bb.goodreads_id_id 
                group by bg."name" 
                order by total desc
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_author_stats():
    with connection.cursor() as cursor:
        query = """
                select br.author, count(br.author) as books, sum(bb.number_of_pages) as pages from books_book bb, books_review br 
                where bb.goodreads_id = br.goodreads_id_id and br.bookshelves = 'read'
                group by br.author 
                having sum(bb.number_of_pages) > 0
                order by pages desc
                limit 20
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_author_awards():
    with connection.cursor() as cursor:
        query = """
                SELECT br.author, bb.title, COUNT(baw.goodreads_id_id) AS awards, br.goodreads_id_id as book_id
                FROM books_award baw
                JOIN books_review br ON br.goodreads_id_id = baw.goodreads_id_id
                JOIN books_book bb ON bb.goodreads_id = br.goodreads_id_id
                WHERE br.bookshelves = 'read'
                GROUP BY br.author, bb.title, book_id
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_author_awards_count():
    with connection.cursor() as cursor:
        query = """
                SELECT count(distinct br.author) as total
                FROM books_award baw
                JOIN books_review br ON br.goodreads_id_id = baw.goodreads_id_id
                JOIN books_book bb ON bb.goodreads_id = br.goodreads_id_id
                WHERE br.bookshelves = 'read'
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_awards_data(request, book_id):
    """
    ajax endpoint triggered by the awards chart
    """
    awards = list(Award.objects.filter(goodreads_id_id=book_id).values('name', 'awarded_at'))

    return JsonResponse({'awards': awards})


def get_books_popularity():
    with connection.cursor() as cursor:
        query = """
                SELECT br.author, bb.title, bb.ratings_count, br.goodreads_id_id as book_id from
                books_review br
                JOIN books_book bb ON bb.goodreads_id = br.goodreads_id_id
                WHERE br.bookshelves = 'read'
                GROUP BY br.author, bb.title, bb.ratings_count, book_id
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_total_pages_count():
    with connection.cursor() as cursor:
        query = """
                select sum(bb.number_of_pages) from books_book bb, books_review br 
                where bb.goodreads_id = br.goodreads_id_id and br.bookshelves = 'read'
        """
        cursor.execute(query)
        results = cursor.fetchone()

        return results


def book_stats(request):
    """
    function used to retrieve data about books using the queries above
    renders different statistics in one page
    """
    monthly_data = get_monthly_stats()
    pub_stats = get_pub_stats()
    yearly_stats = get_yearly_stats()
    genre_stats = get_genres_stats()
    genre_stats_year = get_genres_stats_by_year()
    genre_category = get_genres_cat()

    awards = get_author_awards()
    awards_count = get_author_awards_count()
    ratings = get_books_popularity()
    author_pages = get_author_stats()
    pages_number = get_total_pages_count()

    context = {'monthlyData': monthly_data, 'pubStats': pub_stats, 'yearStats': yearly_stats, 'genreStats': genre_stats,
               'genreStatsYear': genre_stats_year, 'genreCategory': genre_category, 'author_pages': list(author_pages),
               'awards': awards, 'awards_count': awards_count, 'ratings': ratings, 'pages': pages_number}

    return render(request, "stats/book_stats.html", context)


def get_book_locations():
    with connection.cursor() as cursor:
        query = """
                select bb.title, br.bookshelves, br.original_publication_year, bl."name", bl.code, bl.latitude, bl.longitude 
                from books_book bb, books_review br, books_location bl, books_booklocation bb2
                where br.bookshelves in ('read', 'to-read') and bl.updated is true and
                bb.goodreads_id = br.goodreads_id_id and bl.id = bb2.location_id_id and bb2.goodreads_id_id = bb.goodreads_id
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_book_locations_stats():
    with connection.cursor() as cursor:
        query = """
                select bl."name", count(bb.goodreads_id_id) as places_count  from books_location bl, books_booklocation bb, books_review br
                where bl.id = bb.location_id_id and bb.goodreads_id_id = br.id 
                and bl.updated = 'True' and br.bookshelves in ('read', 'to-read')
                group by bl."name" 
                order by places_count desc
                limit 15
        """
        cursor.execute(query)
        results = cursor.fetchall()

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
    queryset = Location.objects.filter(requested=False)

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

    queryset_adv = Location.objects.filter(requested=False)

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


class MapBookView(View):
    def get(self, request, *args, **kwargs):
        """
        queries the db for locations which lack geocoding data (requested = false)
        if empty, set value to 0 and hide Get location data info in js file
        """

        queryset = Location.objects.filter(requested=False)
        empty_loc = len(queryset) or 0
        location_stats = get_book_locations_stats()

        raw_data = get_book_locations()
        locations_data = []

        for item in raw_data:
            location = {
                'title': item[0],
                'status': item[1],
                'year': item[2],
                'location_name': item[3],
                'country_code': item[4],
                'latitude': item[5],
                'longitude': item[6]
            }

            for key, value in location.items():
                if value is None:
                    location[key] = 'None'

            locations_data.append(location)

        context = {'emptyLoc': empty_loc, 'queryset': queryset, 'locations': locations_data,
                   'locations_stats': location_stats
                   }

        return render(request, "books/book_map.html", context)

    def post(self, request, *args, **kwargs):
        """
        queries the OpenStreetMap data for locations which lack geocoding data (requested = false) using Nominatim
        DEPRECATED
        """
        return render(request, "books/book_map.html")


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


def get_author_locations():
    with connection.cursor() as cursor:
        query = """
                select ba."name", ba2."name" as place, ba2.code, ba2.latitude, ba2.longitude  
                from books_author ba, books_authorlocation ba2, books_authloc ba3
                where ba.author_id = ba3.author_id_id and ba2.id = ba3.authorlocation_id_id and
                ba2.updated is true
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results


def get_author_locations_stats():
    with connection.cursor() as cursor:
        query = """
                select ba2."name" , count(authorlocation_id_id) as places_count from books_authloc ba, books_authorlocation ba2 
                where ba.authorlocation_id_id = ba2.id and ba2.updated = 'True'
                group by ba2."name" 
                order by places_count desc
                limit 15
        """
        cursor.execute(query)
        results = cursor.fetchall()

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


class AuthorMapView(View):
    """
    extract NER data from author's description
    I haven't found a good use for other ner entities yet
    """
    def get(self, request, *args, **kwargs):

        queryset = Author.objects.filter(processed_ner=False)
        empty_loc = len(queryset) or 0
        location_stats = get_author_locations_stats()

        raw_data = get_author_locations()
        locations_data = []

        for item in raw_data:
            location = {
                'name': item[0],
                'location_name': item[1],
                'country_code': item[2],
                'latitude': item[3],
                'longitude': item[4]
            }
            # Handle null values
            for key, value in location.items():
                if value is None:
                    location[key] = 'None'

            locations_data.append(location)

        context = {'emptyLoc': empty_loc, 'queryset': queryset, 'locations': locations_data,
                   'locations_stats': location_stats}

        return render(request, "authors/author_map.html", context)

    def post(self, request, *args, **kwargs):
        queryset = Author.objects.filter(processed_ner=False)

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

    author_location = AuthorLocation.objects.get(name=location)
    latitude = author_location.latitude
    longitude = author_location.longitude
    matching_locations = AuthorLocation.objects.filter(latitude=latitude, longitude=longitude)
    authors = list(Author.objects.filter(authloc__authorlocation_id__in=matching_locations).values('name'))

    return JsonResponse({'authors': authors})


def get_books_map_data(request, location):
    """
    function which is triggered by markers and clusters in the book map view
    It returns books ordered by original publication year and their shelf, which will get sorted in the .js file
    """

    books_location = Location.objects.get(name=location)
    latitude = books_location.latitude
    longitude = books_location.longitude
    matching_locations = Location.objects.filter(latitude=latitude, longitude=longitude)

    books = list(
        Book.objects.filter(booklocation__location_id__in=matching_locations, review__isnull=False)
        .annotate(
            publication_year=F('review__original_publication_year'),
            shelf=F('review__bookshelves')
        )
        .order_by('publication_year')
        .values('title', 'publication_year', 'shelf')
    )

    return JsonResponse({'books': books})


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


def quotes_page(request):
    """
    renders the main page of quotes
    I tried adding paginators, but it messes the masonry.js layout
    """
    tags = (QuoteTag.objects.annotate(total=Count('quotequotetag__quote_id'))
                    .filter(total__gt=0).order_by('-total', 'name'))
    no_tags_count = Quote.objects.annotate(tag_count=Count('quotequotetags')).filter(tag_count=0).count()
    fav_count = Quote.objects.filter(favorite=True).count()
    books = Book.objects.annotate(num_quotes=Count('quote')).filter(num_quotes__gt=0).order_by('title')

    context = {'tags': tags, 'no_tags_count': no_tags_count, 'fav_count': fav_count, 'books': books}

    return render(request, 'books/quotes.html', context)


def quotes_tag_filter(request):
    """
    returns quotes containing the selected tag and handles the case with quotes with no tags
    """
    tag = request.GET.get('tag')
    quotes = None
    if tag == "no_tag":
        quotes = Quote.objects.annotate(tag_count=Count('quotequotetags')).filter(tag_count=0).select_related('book')
        tag_name = "No Tags"
    else:
        tag_name = get_object_or_404(QuoteTag, name=tag)
        quotes = Quote.objects.filter(quotequotetags__tag_id=tag_name).select_related('book')

    context = {'quotes': quotes, 'tag': tag_name}
    return render(request, 'partials/books/quotes/quotes.html', context)


def quotes_favorite_filter(request):
    """
    returns favorite quotes
    """
    quotes = Quote.objects.filter(favorite=True)
    context = {'quotes': quotes, 'fav_title': "Favorite quotes"}

    return render(request, 'partials/books/quotes/quotes.html', context)


def quotes_book_filter(request, book_id):
    """
    returns quotes from the selected book
    """
    book = get_object_or_404(Book.objects.prefetch_related('quote_set'), goodreads_id=book_id)
    quotes = book.quote_set.all().order_by('-favorite', 'id')
    book_title = book.title

    context = {'quotes': quotes, 'book_title': book_title}

    return render(request, 'partials/books/quotes/quotes.html', context)


def quotes_update_fav_sidebar(request):
    """
    updates the favorites count in the left sidebar
    """
    fav_count = Quote.objects.filter(favorite=True).count()
    context = {'fav_count': fav_count}

    return render(request, 'partials/books/quotes/fav_quotes_sidebar.html', context)


def quotes_update_books_sidebar(request):
    """
    updates the book list in the left sidebar
    """
    books = Book.objects.annotate(num_quotes=Count('quote')).filter(num_quotes__gt=0).order_by('title')
    context = {'books': books}

    return render(request, 'partials/books/quotes/book_list_sidebar.html', context)


def quotes_update_tags_sidebar(request):
    """
    updates the tags count in the right sidebar
    """
    tags = (QuoteTag.objects.annotate(total=Count('quotequotetag__quote_id'))
            .filter(total__gt=0).order_by('-total', 'name'))
    no_tags_count = Quote.objects.annotate(tag_count=Count('quotequotetags')).filter(tag_count=0).count()

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
    search_text = request.GET.get('search')
    quotes = Quote.objects.filter(text__icontains=search_text)
    results_no = quotes.count()

    for quote in quotes:
        quote.text = highlight_search_term(quote.text, search_text)

    context = {'quotes': quotes, "search_text": search_text, 'results_no': results_no}
    return render(request, 'partials/books/quotes/quotes.html', context)
