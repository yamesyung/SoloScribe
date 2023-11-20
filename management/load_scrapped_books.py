import pandas as pd
import json
import psycopg2
import sqlalchemy

if __name__ == '__main__':

    with open(r'/home/john/Desktop/books.jl') as f:
        lines = f.read().splitlines()

    df_inter = pd.DataFrame(lines)
    df_inter.columns = ['json_element']

    df_inter['json_element'].apply(json.loads)
    df = pd.json_normalize(df_inter['json_element'].apply(json.loads))

    df = df.drop(['titleComplete','imageUrl','asin','isbn','isbn13','series','ratingHistogram','language','awards'], axis=1)

    df = df.fillna(-1)

    df['goodreads_id'] = df['url'].str.extract(r'([0-9]+)')
    df = df[['url','goodreads_id','title','description','genres','author','publishDate','publisher','characters','ratingsCount','reviewsCount','numPages','places']]

    df = df.rename(columns={'publishDate':'publish_date','ratingsCount':'rating_counts','reviewsCount':'review_counts','numPages':'number_of_pages'})


    df = df.astype({'url':'string','goodreads_id':'Int64','title':'string','description':'string','genres':'string','author':'string','publish_date':'datetime64[ms]','publisher':'string','characters':'string','number_of_pages':'Int32','places':'string'})
    print(df.dtypes)

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