import os
import re
import csv
import shutil
import pandas as pd
from csv import DictReader
from io import StringIO, TextIOWrapper
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.db.models.functions import Lower

from accounts.models import Theme, UserPreferences
from .models import CustomUser
from .forms import CustomUserCreationForm, ImportForm, ReviewForm
from books.models import Book, Review, UserTag, ReviewTag, Quote, QuoteTag, QuoteQuoteTag


def format_date(date):
    """
    function used to process date fields when importing the csv file
    """
    return datetime.strptime(date, '%Y/%m/%d').strftime('%Y-%m-%d')


def get_theme_list():
    """
    Returns a list of available themes (directories under static/themes)
    and ensures they exist in the Theme model.
    """
    theme_dir_path = os.path.join(settings.BASE_DIR, 'static', 'themes')

    try:
        theme_list = [
            d for d in os.listdir(theme_dir_path)
            if os.path.isdir(os.path.join(theme_dir_path, d))
        ]
    except FileNotFoundError:
        theme_list = []

    for theme in theme_list:
        Theme.objects.get_or_create(name=theme)

    return theme_list


def add_custom_theme_files(user):
    """
    function that adds files and directories for user custom theme in static/users/<user_id>/css
    used when creating a new profile or logging in and the files are missing.
    """
    # Create user theme directory
    user_theme_dir = os.path.join(settings.BASE_DIR, 'static', 'users', str(user.id), 'css')
    os.makedirs(user_theme_dir, exist_ok=True)

    # Copy the default files for custom theme
    default_path = os.path.join(settings.BASE_DIR, 'static', 'themes', 'custom', 'css')

    for filename in ["base.css", "cover.jpg", "font.ttf"]:
        src_file = os.path.join(default_path, filename)
        dst_file = os.path.join(user_theme_dir, filename)

        # Only copy if destination file doesn't exist
        if os.path.exists(src_file) and not os.path.exists(dst_file):
            shutil.copy2(src_file, dst_file)


def login_page(request):
    """
    renders main page for profiles
    """
    accounts = CustomUser.objects.all().order_by(Lower("username"))
    context = {'accounts': accounts}

    return render(request, 'account/login_page.html', context)


def create_profile(request):
    """
    creates a new profile with the given username and password. It also creates the user-preferences table
    and a folder with the required files for custom theme
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create the user preferences table
            UserPreferences.objects.create(user=user)
            # Create user theme directory and files
            add_custom_theme_files(user)

            response = HttpResponse()
            response['HX-Redirect'] = '/accounts/login-page/'
            return response
    else:
        form = CustomUserCreationForm()

    return render(request, "partials/account/create_user_form.html", {"form": form})


def login_form(request):
    """
    renders a form for the login
    """
    username = request.GET.get("username", "")
    context = {"username": username}

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Adds user custom theme files if missing
            add_custom_theme_files(user)

            response = HttpResponse()
            response['HX-Redirect'] = '/'
            return response
        else:
            return render(request, "partials/account/login_form.html", {
                "username": username,
                "error": "Invalid password"
            })

    return render(request, "partials/account/login_form.html", context)


def logout_view(request):
    logout(request)

    return redirect('login_page')


def settings_page(request):
    books_to_scrape_count = Book.objects.filter(scrape_status=False, review__user=request.user).count()
    form = ImportForm()
    context = {'form': form, 'books_to_scrape_count': books_to_scrape_count}
    return render(request, 'account/settings.html', context)


def profile_settings(request):
    return render(request, 'partials/account/settings/profile_settings.html')


def change_username_form(request):
    return render(request, 'partials/account/settings/change_username_form.html')


@login_required
def change_username(request):
    if request.method == "POST":
        new_username = request.POST.get("new_username")
        password = request.POST.get("password")

        user = authenticate(username=request.user.username, password=password)
        if not user:
            return render(request, 'partials/account/settings/change_username_form.html', {
                'error': 'Incorrect password.'
            })

        if not new_username:
            return render(request, 'partials/account/settings/change_username_form.html', {
                'error': 'Username cannot be empty.'
            })

        if CustomUser.objects.filter(username=new_username).exists():
            return render(request, 'partials/account/settings/change_username_form.html', {
                'error': 'This username is already taken.'
            })

        request.user.username = new_username
        request.user.save()

        update_session_auth_hash(request, request.user)
        response = HttpResponse()
        response['HX-Redirect'] = '/accounts/settings/'
        return response

    return redirect("settings")


def change_password_form(request):
    return render(request, 'partials/account/settings/change_password_form.html')


@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        user = request.user

        if not user.check_password(old_password):
            return render(request, 'partials/account/settings/change_password_form.html', {
                'error': 'Current password is incorrect.'
            })

        if new_password1 != new_password2:
            return render(request, 'partials/account/settings/change_password_form.html', {
                'error': 'New passwords do not match.'
            })

        user.set_password(new_password1)
        user.save()

        update_session_auth_hash(request, user)

        response = HttpResponse()
        response['HX-Redirect'] = '/accounts/settings/'
        return response

    return redirect("settings")


def delete_profile_form(request):
    return render(request, 'partials/account/settings/delete_profile_form.html')


@login_required
def delete_profile(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        user = request.user

        if not user.check_password(password):
            return render(request, 'partials/account/settings/delete_profile_form.html', {
                'error': 'Incorrect password.'
            })

        if confirm != "DELETE":
            return render(request, 'partials/account/settings/delete_profile_form.html', {
                'error': 'You must type DELETE to confirm.'
            })

        # delete user's theme directory
        user_theme_dir = os.path.join(settings.BASE_DIR, 'static', 'users', str(user.id))
        if os.path.exists(user_theme_dir):
            shutil.rmtree(user_theme_dir)

        user.delete()
        logout(request)

        response = HttpResponse()
        response['HX-Redirect'] = '/accounts/login-page/'
        return response

    return redirect("settings")


def delete_user_data_form(request):
    return render(request, 'partials/account/settings/delete_user_data_form.html')


@login_required
def delete_user_data(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        user = request.user

        if not user.check_password(password):
            return render(request, 'partials/account/settings/delete_profile_form.html', {
                'error': 'Incorrect password.'
            })

        if confirm != "DELETE":
            return render(request, 'partials/account/settings/delete_profile_form.html', {
                'error': 'You must type DELETE to confirm.'
            })

        Review.objects.filter(user=user).delete()

        response = HttpResponse()
        response['HX-Redirect'] = '/accounts/settings/'
        return response

    return redirect("settings")


def themes_settings(request):
    """
    returns a list of folders from static/themes which contains the static files of the theme (css/js/images/fonts)
    saves the name of new folders in the model, but returns only the current folders
    """
    theme_list = get_theme_list()

    context = {"theme_list": theme_list}

    return render(request, 'partials/account/settings/theme_settings.html', context)


@login_required
def change_active_theme(request):
    """
    Change the current user's preferred theme.
    """
    if request.method == "POST":
        selected_theme_name = request.POST.get("theme")
        if not selected_theme_name:
            return redirect("settings")  # no theme selected

        theme = get_object_or_404(Theme, name=selected_theme_name)

        prefs, _ = UserPreferences.objects.get_or_create(user=request.user)

        prefs.preferred_theme = theme
        prefs.save()

    theme_list = get_theme_list()
    context = {"theme_list": theme_list}

    return render(request, 'account/settings.html', context)


@login_required
def change_cover(request):
    """
    save an uploaded image as cover.jpg for the logged-in user
    """
    if request.method == 'POST' and request.FILES.get('background-file'):
        uploaded_file = request.FILES['background-file']
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        if file_extension == ".jpg":
            new_filename = f'cover{file_extension}'

            user_dir = os.path.join(settings.BASE_DIR, 'static', 'users', str(request.user.id), 'css')
            os.makedirs(user_dir, exist_ok=True)

            file_path = os.path.join(user_dir, new_filename)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            theme_list = get_theme_list()
            context = {"theme_list": theme_list}

            return render(request, 'account/settings.html', context)

    return redirect('settings')


@login_required
def change_font(request):
    """
    save an uploaded font as font.ttf for the logged-in user
    """
    if request.method == 'POST' and request.FILES.get('font-file'):
        uploaded_file = request.FILES['font-file']
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()

        if file_extension == ".ttf":
            new_filename = f'font{file_extension}'

            user_dir = os.path.join(settings.BASE_DIR, 'static', 'users', str(request.user.id), 'css')
            os.makedirs(user_dir, exist_ok=True)

            file_path = os.path.join(user_dir, new_filename)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            theme_list = get_theme_list()
            context = {"theme_list": theme_list}

            return render(request, 'account/settings.html', context)

    return redirect('settings')


@login_required
def change_text_color(request):
    """
    save the color input from the form as a css variable in :root in the base.css of the logged-in user
    """
    if request.method == 'POST':
        color = request.POST.get('textColor', '#ff0000')

        if color != "rgba(0, 0, 0, 0)":  # handle null RGB values from some color pickers
            user_dir = os.path.join(settings.BASE_DIR, 'static', 'users', str(request.user.id), 'css')
            os.makedirs(user_dir, exist_ok=True)

            css_filepath = os.path.join(user_dir, 'base.css')

            # update font variable
            try:
                with open(css_filepath, 'r+') as css_file:
                    css_content = css_file.read()

                    updated_content = re.sub(
                        r'(--font-color:\s*)(#[0-9a-fA-F]{6});',
                        rf'\1{color};',
                        css_content
                    )

                    css_file.seek(0)
                    css_file.write(updated_content)
                    css_file.truncate()

            except FileNotFoundError:
                print(f"CSS file not found: {css_filepath}")

            theme_list = get_theme_list()
            context = {"theme_list": theme_list}

            return render(request, 'account/settings.html', context)

    return redirect('settings')


def import_data_settings(request):
    books_to_scrape_count = Book.objects.filter(scrape_status=False, review__user=request.user).count()
    form = ImportForm()
    context = {'form': form, 'books_to_scrape_count': books_to_scrape_count}
    return render(request, 'partials/account/settings/import_data_settings.html', context)


@login_required()
def import_review_data(request):
    if request.method == 'POST':
        csv_file = request.FILES["goodreads_file"]
        ignore_shelf = request.POST.get('ignore-shelf') == 'on'

        try:
            file_data = csv_file.read().decode("utf-8")
            rows = StringIO(file_data)
            reader = csv.DictReader(rows)
        except Exception as e:
            return render(request, 'partials/account/settings/import_data_form.html', {
                'error': f"Error reading CSV file: {e}"
            })

        required_headers = {'Book Id', 'Title', 'Author', 'ISBN', 'ISBN13', 'My Rating', 'Exclusive Shelf'}
        file_headers = set(reader.fieldnames or [])

        missing = required_headers - file_headers
        if missing:
            return render(request, 'partials/account/settings/import_data_form.html', {
                'error': f"Missing required columns: {', '.join(missing)}"
            })

        rows.seek(0)
        reader = csv.DictReader(rows)

        imported_count = 0
        for row in reader:
            shelf = (row.get('Exclusive Shelf') or '').strip().lower()
            if ignore_shelf and shelf == "to-read":
                continue

            review_data = {
                'book': row['Book Id'],
                'title': row['Title'],
                'user': request.user,
                'author': row['Author'],
                'additional_authors': row['Additional Authors'],
                'isbn': row['ISBN'],
                'isbn13': row['ISBN13'],
                'rating': row['My Rating'],
                'year_published': row['Year Published'],
                'original_publication_year': row['Original Publication Year'],
                'date_read': row['Date Read'],
                'date_added': row['Date Added'],
                'bookshelves': row['Exclusive Shelf'],
                'review_content': re.sub(r'<br\s*?/?>', '\n', row['My Review']),
                'private_notes': row['Private Notes'],
                'read_count': row['Read Count'],
                'owned_copies': row['Owned Copies'],
                'author_lf': row['Author l-f'],
                'average_rating': row['Average Rating'],
                'publisher': row['Publisher'],
                'binding': row['Binding'],
                'number_of_pages': row['Number of Pages'],
                'user_shelves': row['Bookshelves'],
                'user_shelves_positions': row['Bookshelves with positions'],
                'spoiler': row['Spoiler']
            }

            if review_data['isbn']:
                review_data['isbn'] = review_data['isbn'].replace('="', '').replace('"', '')

            if review_data['isbn13']:
                review_data['isbn13'] = review_data['isbn13'].replace('="', '').replace('"', '')

            if review_data['date_read']:
                review_data['date_read'] = format_date(review_data['date_read'])
            review_data['date_added'] = format_date(review_data['date_added'])

            book, created = Book.objects.get_or_create(
                goodreads_id=review_data['book'],
                defaults={'title': review_data['title']}
            )

            review_exists = Review.objects.filter(user=request.user, book=book).exists()

            if not review_exists:
                form = ReviewForm(review_data)
                review = form.save()
                imported_count += 1

                if review_data['user_shelves']:
                    tag_list = review_data['user_shelves'].split(',')

                    for tag in tag_list:
                        tag = tag.strip()
                        tag_obj, created = UserTag.objects.get_or_create(name=tag)

                        reviewtag_obj, created = ReviewTag.objects.get_or_create(review=review, tag=tag_obj)

        return redirect("settings")

    return redirect("settings")


@login_required()
def import_quotes_csv(request):
    """
    Import quotes data for the current user
    """
    if request.method == 'POST' and request.FILES.get('quotes-file'):
        uploaded_file = request.FILES['quotes-file']
        match_quote_url = request.POST.get('quotes-url') == 'on'
        rows = TextIOWrapper(uploaded_file, encoding="utf-8", newline="")

        for row in DictReader(rows):
            book_id = row['Book Id']
            quote_page = int(float(row['Page'])) if row['Page'] else None
            quote_date = format_date(row['Date Added']) if row['Date Added'] else None
            tags_data = row['Tags'].split(',') if row['Tags'] else []
            quote_text = row['Content']
            quote_url = row.get('Quotes Url', '').strip()
            favorite = row['Favorite'].lower() == 'true' if row['Favorite'] else False

            try:
                if match_quote_url and quote_url:
                    review = Review.objects.get(book__quotes_url=quote_url, user=request.user)
                else:
                    review = Review.objects.get(book__goodreads_id=book_id, user=request.user)
            except Review.DoesNotExist:
                print(f"No existing review for book ID {book_id} by user {request.user}. Skipping quote: {quote_text}")
                continue

            quote = Quote.objects.create(
                review=review,
                text=quote_text,
                date_added=quote_date,
                page=quote_page,
                favorite=favorite
            )

            tag_names = {tag.strip() for tag in tags_data if tag.strip()}
            for tag_name in tag_names:
                quote_tag, _ = QuoteTag.objects.get_or_create(name=tag_name)
                QuoteQuoteTag.objects.create(quote_id=quote, tag_id=quote_tag)

        return redirect("quotes_page")


def export_settings(request):
    return render(request, 'partials/account/settings/export_settings.html')


def export_csv_goodreads(request):
    """
    creates a csv file containing updated data with a similar format to the goodreads export library's file.
    Theoretically, you can import it back to goodreads, but it is not reliable (goodreads import problems)
    """
    user = request.user
    queryset = Review.objects.filter(user=user)

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


def export_quotes_csv(request):
    """
    creates a csv file containing quotes data
    """
    user = request.user
    quotes = (
        Quote.objects
        .filter(review__user=user, review__bookshelves__iexact='read')
        .select_related('review__book')
        .prefetch_related(
            Prefetch(
                'quotequotetags',
                queryset=QuoteQuoteTag.objects.select_related('tag_id')
            )
        )
    )

    data = []

    for quote in quotes:
        review = quote.review
        book = review.book
        tags = ", ".join(qqt.tag_id.name for qqt in quote.quotequotetags.all())

        data.append({
            'Book Id': book.goodreads_id,
            'Title': book.title,
            'Author': book.author,
            'Page': quote.page,
            'Date Added': quote.date_added.strftime('%Y/%m/%d') if quote.date_added else '',
            'Favorite': quote.favorite or None,
            'Tags': tags,
            'Content': quote.text,
            'Quotes Url': book.quotes_url
        })
    df = pd.DataFrame(data)

    csv_buffer = df.to_csv(index=False).encode('utf-8')

    response = HttpResponse(csv_buffer, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="quotes.csv"'
    return response


@login_required()
def update_gallery_cover_size(request):
    try:
        size = int(request.GET.get('size'))
        if 100 <= size <= 240:
            preferences, created = UserPreferences.objects.get_or_create(
                user=request.user
            )
            preferences.gallery_cover_size = size
            preferences.save()
            return HttpResponse(status=204)
        else:
            return HttpResponse("Invalid size", status=400)
    except (ValueError, TypeError, AttributeError):
        return HttpResponse("Invalid size", status=400)
