import pandas as pd
import ast
import json
import psycopg2
import sqlalchemy

"""
    scripts used to load data into db before file upload, left for reference
"""

if __name__ == '__main__':

    with open(r'/home/john/Desktop/books.jl') as f:
        lines = f.read().splitlines()

    df_inter = pd.DataFrame(lines)
    df_inter.columns = ['json_element']

    df_inter['json_element'].apply(json.loads)
    df = pd.json_normalize(df_inter['json_element'].apply(json.loads))

    df = df.drop(['titleComplete', 'asin', 'isbn', 'isbn13'], axis=1)
    df[['numPages', 'publishDate']] = df[['numPages', 'publishDate']].fillna(-1)
    df = df.fillna("")

    df['goodreads_id'] = df['url'].str.extract(r'([0-9]+)')
    df['last_uploaded'] = pd.to_datetime('now')

    df = df[['url','goodreads_id','title','description','genres','author','publishDate','publisher','characters','ratingsCount','reviewsCount','numPages','places', 'imageUrl', 'ratingHistogram', 'language', 'awards', 'series', 'last_uploaded']]

    df = df.rename(columns={'publishDate': 'publish_date', 'ratingsCount': 'rating_counts', 'reviewsCount': 'review_counts', 'numPages': 'number_of_pages', 'imageUrl': 'image_url', 'ratingHistogram': 'rating_histogram'})

    df = df.astype({'url':'string','goodreads_id':'Int64','title':'string','description':'string','genres':'string','author':'string','publish_date':'datetime64[ms]','publisher':'string','characters':'string',
                    'number_of_pages':'Int32','places':'string','image_url':'string','rating_histogram':'string','language':'string','awards':'string','series':'string'})

    count = 0

    for index, row in df.iterrows():
        if row['awards']:
            print(row['awards'])
            awards = [(item["name"], item["awardedAt"]) for item in ast.literal_eval(row['awards'])]
            for name, awardedAt in awards:
                print(name, awardedAt)
                count += 1
    print(count)

    try:
        conn = psycopg2.connect(
            host='localhost',
            port='54320',
            database='postgres',
            user='postgres',
            password='postgres'
        )

        print('DB connected')
    except:
        print('DB not connected')
        raise

    curr = conn.cursor()
    engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:postgres@localhost:54320/postgres')

    try:
        df.to_sql("books_book", engine, "public", index=False, if_exists='append')
        print('loaded')
    except:
        print('cannot be loaded')

    if conn:
        curr.close()
        conn.close()
        print("PostgreSQL connection is closed")