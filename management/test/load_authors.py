import pandas as pd
import json
import psycopg2
import sqlalchemy

"""
    scripts used to load data into db before file upload, left for reference
"""
if __name__ == '__main__':

    def remove_subset(a):
        return [x for x in a if not any(x in y and x != y for y in a)]

    def clear_empty_lists(x):
        if x == ['[', ']']:
            return []
        else:
            return x

    def remove_more_suffix(x):
        if x.endswith("...more"):
            return x[:-8]
        else:
            return x

    word_to_filter = "(^.*/[blog]+.*$)"
    word_to_filter2 = "(^.*\?[tab]+.*$)"
    word_to_filter3 = "(^.*\?[order]+.*$)"

    with open(r'/home/john/Desktop/authors.jl') as f:
        lines = f.read().splitlines()

    df_inter = pd.DataFrame(lines)
    df_inter.columns = ['json_element']

    df_inter['json_element'].apply(json.loads)
    df = pd.json_normalize(df_inter['json_element'].apply(json.loads))

    df[['birthDate', 'deathDate']] = df[['birthDate', 'deathDate']].fillna('01-01-0001')

    df[['influences','genres']] = df[['influences','genres']].fillna('[]')
    df['influences'] = df['influences'].apply(remove_subset)
    df['influences'] = df['influences'].apply(clear_empty_lists)

    df['reviewsCount'] = df['reviewsCount'].fillna(0)
    df['ratingsCount'] = df['ratingsCount'].fillna(0)
    df['avgRating'] = df['avgRating'].fillna(0)

    df = df.fillna("")
    df['author_id'] = df['url'].str.extract(r'([0-9]+)')

    df = df[['url', 'author_id', 'name', 'birthDate', 'deathDate', 'genres', 'influences', 'avgRating', 'reviewsCount', 'ratingsCount', 'about']]
    df = df.rename(columns={'birthDate':'birth_date','deathDate':'death_date','avgRating':'avg_rating','reviewsCount':'reviews_count','ratingsCount':'rating_count'})
    df = df.astype({'url':'string','author_id':'Int64','name':'string','genres':'string','influences':'string','birth_date':'string','death_date':'string','reviews_count':'Int64','rating_count':'Int64','about':'string'})

    df['about'] = df['about'].apply(remove_more_suffix)

    filtered = df['url'].str.contains(word_to_filter)
    df = df[~filtered]

    filtered2 = df['url'].str.contains(word_to_filter2)
    df = df[~filtered2]

    filtered3 = df['url'].str.contains(word_to_filter3)
    df = df[~filtered3]

    df.drop_duplicates(subset='author_id', inplace=True)
    df.drop_duplicates(subset='name', inplace=True)

    r = df.shape[0]

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
        print(f" {r} items added")

    except:
        print('cannot be loaded')

    if conn:
        curr.close()
        conn.close()
        print("PostgreSQL connection is closed")