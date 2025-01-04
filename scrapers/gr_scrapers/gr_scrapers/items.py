# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import json
from typing import Any, Dict
from datetime import datetime

from scrapy import Field
from scrapy.loader import ItemLoader
from itemloaders.processors import Compose, MapCompose, Identity, TakeFirst, Join
from w3lib.html import remove_tags
from dateutil.parser import parse as dateutil_parse

DEBUG = False


def visit_path(data: Dict[str, Any], key: str, original_key: str):
    if DEBUG:
        print(f"Processing {key} for {data.keys() if type(data) == dict else data}")

    if not data:
        if key and DEBUG:
            print(f'No data found for key {original_key} in data')
            print(data)
        return None

    # if no key is left, then yield the data at this point
    if not key:
        yield data
        # stop the generator since there is no more key left to parse
        return None

    if '.' in key:
        idx = key.index('.')
        subkey, remaining_key = key[:idx], key[idx + 1:]
    else:
        subkey, remaining_key = key, None

    # handle partial matches on the key
    # this is needed when the key can be dynamic
    if subkey.endswith('*'):
        # remove '*'
        subkey_prefix = subkey[:-1]

        # find all keys which match subkey_prefix
        matching_subkeys = [k for k in data.keys() if k.startswith(subkey_prefix)]

        for sk in matching_subkeys:
            yield from visit_path(data[sk], remaining_key, original_key)

        return None

    # handle arrays
    if subkey.endswith('[]'):
        # remove '[]'
        subkey = subkey[:-2]

        values = data.get(subkey, [])

        for value in values:
            yield from visit_path(value, remaining_key, original_key)

        return None

    # handle multiple comma-separated keys
    # this must be the leaf, because it doesn't make sense to extract more fields
    # from differently keyed values (at least for now)
    if subkey.startswith('[') and subkey.endswith(']'):
        subkeys = subkey[1:-1].split(",")
        value = {}
        for sk in subkeys:
            value[sk] = data.get(sk, None)
        yield value

        return None

    # handle regular keys
    yield from visit_path(data.get(subkey, None), remaining_key, original_key)

    return None


def json_field_extractor(key: str):
    def extract_field(text: str):
        data = json.loads(text)
        return list(visit_path(data, key, key))
    return extract_field


def safe_parse_date(date):
    try:
        date = dateutil_parse(date, fuzzy=True, default=datetime.min)
        date = date.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        date = None

    return date


def parse_datetime(timestamp):
    if timestamp:
        try:
            timestamp = timestamp / 1000

            if timestamp < -62135596800:  # for negative years
                return None

            date = datetime.fromtimestamp(timestamp)
            return date
        except (ValueError, OverflowError):
            return None
    return None


def split_by_newline(txt):
    return txt.split("\n")


def filter_empty(vals):
    return [v.strip() for v in vals if v.strip()]


def remove_quotations(word):
    return word.replace(u"\u201d", ' ').replace(u"\u201c", ' ')


def remove_spaces(author_value):
    return author_value[5:-2].strip('\n')


class BookItem(scrapy.Item):
    # Scalars
    url = Field()
    book_id = Field()
    title = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.title')))
    titleComplete = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.titleComplete')))
    description = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.description'), remove_tags))
    imageUrl = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.imageUrl')))
    genres = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.bookGenres[].genre.name')), output_processor=Compose(set, list))
    asin = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.details.asin')))
    isbn = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.details.isbn')))
    isbn13 = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.details.isbn13')))
    publisher = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.details.publisher')))
    publishDate = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.details.publicationTime'), parse_datetime))
    series = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Series*.title')), output_processor=Compose(set, list))

    quotesUrl = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Work*.quotes*.webUrl')))
    firstPublished = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Work*.details.publicationTime'), parse_datetime))
    format = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.details.format')))

    author = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Contributor*.name')), output_processor=Compose(set, list))

    places = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Work*.details.places[].name')), output_processor=Compose(set, list))
    characters = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Work*.details.characters[].name')), output_processor=Compose(set, list))
    awards = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Work*.details.awardsWon[].[name,awardedAt,category,hasWon]')), output_processor=Identity())

    ratingsCount = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Work*.stats.ratingsCount')))
    reviewsCount = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Work*.stats.textReviewsCount')))
    avgRating = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Work*.stats.averageRating')))
    ratingHistogram = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Work*.stats.ratingsCountDist')))

    numPages = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.details.numPages')))
    language = Field(input_processor=MapCompose(json_field_extractor('props.pageProps.apolloState.Book*.details.language.name')))


class BookLoader(ItemLoader):
    default_output_processor = TakeFirst()


class AuthorItem(scrapy.Item):
    # Scalars
    url = Field()
    name = Field()
    birthDate = Field(input_processor=MapCompose(safe_parse_date))
    deathDate = Field(input_processor=MapCompose(safe_parse_date))
    avgRating = Field(serializer=float)
    ratingsCount = Field(serializer=int)
    reviewsCount = Field(serializer=int)

    # Lists
    genres = Field(output_processor=Compose(set, list))
    influences = Field(output_processor=Compose(set, list))

    # Blobs
    about = Field(
        # Take the first match, remove HTML tags, convert to list of lines, remove empty lines, remove the "edit data" prefix
        input_processor=Compose(TakeFirst(), remove_tags, split_by_newline,
                                filter_empty, lambda s: s[1:]),
        output_processor=Join())


class AuthorLoader(ItemLoader):
    default_output_processor = TakeFirst()


class QuoteItem(scrapy.Item):
    book_id = Field()
    text = scrapy.Field(
        input_processor=MapCompose(str.strip, remove_quotations),
        output_processor=TakeFirst()
    )
    author = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_spaces),
        output_processor=TakeFirst()
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(',')
    )


class QuoteLoader(ItemLoader):
    default_output_processor = TakeFirst()
