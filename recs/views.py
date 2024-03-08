import os
import ast
import json
import pandas as pd

from django.shortcuts import render, redirect, get_object_or_404

from recs.models import RecList, Book, Genre, BookGenre, Location, BookLocation, BookList


def load_recs(request):
    directory = os.path.dirname(os.path.realpath(__file__))

    metadata_df = pd.read_csv(directory + '/.metadata.csv')

    for index, row in metadata_df.iterrows():

        list_obj = RecList(
            name=row['name'],
            type=row['type'],
            category=row['category'],
        )
        list_obj.save()

        filepath = directory + '/data/' + row['filename']

        with open(filepath, 'r') as file:
            lines = file.read().splitlines()

        df_inter = pd.DataFrame(lines)
        df_inter.columns = ['json_element']
        df_inter['json_element'].apply(json.loads)
        df = pd.json_normalize(df_inter['json_element'].apply(json.loads))

        df = df.drop(
            ['titleComplete', 'asin', 'isbn', 'isbn13'],
            axis=1)
        df[['numPages', 'ratingsCount']] = df[['numPages', 'ratingsCount']].fillna(-1)
        df = df.fillna("")

        df['goodreads_id'] = df['url'].str.extract(r'([0-9]+)')

        df['last_uploaded'] = pd.to_datetime('now')

        df = df[['url', 'goodreads_id', 'title', 'description', 'genres', 'author', 'publishDate', 'publisher',
                 'characters', 'ratingsCount', 'reviewsCount', 'numPages', 'places', 'imageUrl',
                 'ratingHistogram', 'language', 'awards', 'series', 'last_uploaded']]

        df = df.astype(
            {'url': 'string', 'goodreads_id': 'Int64', 'title': 'string', 'description': 'string',
             'genres': 'string',
             'author': 'string', 'publishDate': 'datetime64[ms]', 'publisher': 'string', 'characters': 'string',
             'numPages': 'Int64', 'places': 'string', 'imageUrl': 'string', 'ratingHistogram': 'string',
             'language': 'string', 'awards': 'string', 'series': 'string'})

        for index2, row2 in df.iterrows():
            book_obj = Book(
                url=row2['url'],
                goodreads_id=row2['goodreads_id'],
                title=row2['title'],
                description=row2['description'],
                genres=row2['genres'],
                author=row2['author'],
                rating_counts=row2['ratingsCount'],
                number_of_pages=row2['numPages'],
                places=row2['places'],
                image_url=row2['imageUrl'],
            )
            book_obj.save()

            booklist_obj = BookList(list_id=list_obj, goodreads_id=book_obj)
            booklist_obj.save()

            if row2['genres']:
                genres = ast.literal_eval(row2['genres'])

                for genre_name in genres:
                    genre_obj, created = Genre.objects.get_or_create(name=genre_name)

                    book_genre_obj = BookGenre(goodreads_id=book_obj, genre_id=genre_obj)

                    book_genre_obj.save()

            if row2['places']:
                places = ast.literal_eval(row2['places'])

                for place_name in places:
                    place_obj, created = Location.objects.get_or_create(name=place_name)

                    book_location_obj = BookLocation(goodreads_id=book_obj, location_id=place_obj)

                    book_location_obj.save()

    return redirect("import_recs")


def import_page(request):
    return render(request, "recs/import_recs.html")


def clear_recs(request):
    Book.objects.all().delete()
    RecList.objects.all().delete()
    Genre.objects.all().delete()
    Location.objects.all().delete()

    return redirect("import_csv")
