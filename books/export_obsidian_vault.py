import io
import os
import zipfile
import ast

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404

from .models import Book, Author, Genre, UserTag, AuthorLocation, Review, Quote, QuoteTag


def sanitize_filename(title, title_counts):
    """
    sanitizes the filename: replaces "/" chars and increment filenames for books with same title.
    """
    # Replace '/' with '_' ex: Stephen King's 11/22/63
    sanitized_title = title.replace('/', '_')
    # Check if the title has already been encountered
    if sanitized_title in title_counts:
        # Increment the count for this title
        title_counts[sanitized_title] += 1
        # Append count to the filename
        return f"{sanitized_title}_{title_counts[sanitized_title]}"
    else:
        # Initialize count for this title
        title_counts[sanitized_title] = 1
        return sanitized_title


def generate_book_markdown_content(book, user):
    """
    generates the content of a book .md file for Obsidian.
    """

    # get data for the selected book from the related models: review, genres, user-tags and quotes
    try:
        review = get_object_or_404(Review, book=book, user=user)
    except Http404:
        review = None
    genres_queryset = Genre.objects.filter(bookgenre__goodreads_id=book)
    tags = UserTag.objects.filter(reviewtag__review=review)
    quotes = Quote.objects.filter(review=review)

    if review:
        markdown_content = f"## {book.title}\n"
        markdown_content += f"Author: [[{review.author}]]\n"
        markdown_content += f"Genres: "
        for genre in genres_queryset:
            markdown_content += f"[[{genre.name}]] "

        if tags:
            markdown_content += f"\nTags: "
            for tag in tags:
                markdown_content += f"#{tag.name} "

        markdown_content += f"\nGoodreads link: {book.url}\n"
        markdown_content += f"First published: {review.original_publication_year}\n"
        markdown_content += f"Number of pages: {book.number_of_pages}\n"
        markdown_content += f"Shelf: #{review.bookshelves} "
        if review.rating:
            markdown_content += f"Rating: #{review.rating}_stars "
        if review.date_read:
            markdown_content += f"Date read: {review.date_read} "
        if book.cover_local_path:
            markdown_content += f"""\n\n![[{book.goodreads_id}.jpg|200]]\n"""
        else:
            markdown_content += f"""\n\n<img src="{book.image_url}" width="200">\n"""
        markdown_content += f"\n## Description\n{book.description}\n"
        if review.bookshelves == 'read':
            if review.review_content:
                markdown_content += f"## Review\n{review.review_content}\n"

        if quotes:
            markdown_content += f"## Highlights\n"
            for quote in quotes:
                markdown_content += f"\n{quote.text}\n"

                tags = QuoteTag.objects.filter(quotequotetag__quote_id=quote)
                if tags:
                    for tag in tags:
                        markdown_content += f"#{tag.name} "
                    markdown_content += "\n"

        return markdown_content
    return ""


def generate_author_markdown_content(author):
    """
    generates the content of an author .md file for Obsidian.
    """
    markdown_content = f"## {author.name}\n"
    if author.birth_date.year != 1:
        markdown_content += f"Birth date: {author.birth_date.strftime('%d-%m-%Y')}\n"
    if author.death_date.year != 1:
        markdown_content += f"Death date: {author.death_date.strftime('%d-%m-%Y')}\n"
    if author.influences != "[]":
        markdown_content += f"## Influences:\n "
        influences = ast.literal_eval(author.influences)
        for name in influences:
            markdown_content += f"[[{name}]]\n"
    if author.about:
        markdown_content += f"\n## About:\n {author.about}\n"

    if author.processed_ner:
        locations = AuthorLocation.objects.filter(authloc__author_id=author, updated=True)
        if locations:
            markdown_content += f"### Places:\n"
            for location in locations:
                markdown_content += f"[[{location.name}]] "

    return markdown_content


def export_zip_vault(request):
    """
    exports an archive file containing the books and authors in a format structured for Obsidian.
    """
    user = request.user
    # Create an in-memory zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        # Query data from the database ex:
        # Books from a specific shelf:
        # books_queryset = Book.objects.filter(review__bookshelves='read')
        # Books with user data available (default):
        books_queryset = Book.objects.filter(review__user=user)
        # Authors with no blank name
        authors_queryset = Author.objects.filter(book__review__user=user, name__isnull=False).exclude(name="").distinct()

        title_counts = {}

        # Iterate over queryset and generate markdown files
        for book in books_queryset:

            markdown_content = generate_book_markdown_content(book, user)
            file_name = f"books_vault/books/{sanitize_filename(book.title, title_counts)}.md"
            zip_file.writestr(file_name, markdown_content)

            if book.cover_local_path:
                try:
                    cover_path = os.path.join(settings.MEDIA_ROOT, book.cover_local_path)
                    zip_file.write(cover_path, f"books_vault/books/covers/{book.goodreads_id}.jpg")
                except:
                    continue

        for author in authors_queryset:

            markdown_content = generate_author_markdown_content(author)
            file_name = f"books_vault/authors/{author.name}.md"
            zip_file.writestr(file_name, markdown_content)

    # Construct the response with appropriate headers
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="obsidian_vault.zip"'
    response['Content-Length'] = zip_buffer.tell()

    return response
