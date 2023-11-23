import pandas as pd
import json
import psycopg2
import sqlalchemy

if __name__ == '__main__':

    with open(r'/home/john/Desktop/authors.jl') as f:
        lines = f.read().splitlines()

    df_inter = pd.DataFrame(lines)
    df_inter.columns = ['json_element']

    df_inter['json_element'].apply(json.loads)
    df = pd.json_normalize(df_inter['json_element'].apply(json.loads))

    df[['birthDate','deathDate']] = df[['birthDate','deathDate']].fillna('0001-01-01 00:00:00')

    df = df.fillna(-1)
    df['author_id'] = df['url'].str.extract(r'([0-9]+)')

    df = df[['url','author_id','name','birthDate','deathDate','genres','influences','avgRating','reviewsCount','ratingsCount','about']]
    df = df.rename(columns={'birthDate':'birth_date','deathDate':'death_date','avgRating':'avg_rating','reviewsCount':'reviews_count','ratingsCount':'rating_count'})
    df = df.astype({'url':'string','author_id':'Int64','name':'string','genres':'string','influences':'string','birth_date':'string','death_date':'string','reviews_count':'Int64','rating_count':'Int64','about':'string'})



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
        df.to_sql("books_author", engine, "public", index=False, if_exists='append')
        print('loaded')
    except:
        print('cannot be loaded')

    if conn:
        curr.close()
        conn.close()
        print("PostgreSQL connection is closed")