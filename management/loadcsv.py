import pandas as pd
import psycopg2
import sqlalchemy

if __name__ == '__main__':

    data =  pd.read_csv(r'/home/john/Desktop/library.csv')
    df = pd.DataFrame(data, columns=['Book Id', 'Title', 'Author', 'Publisher', 'Number of Pages', 'Year Published', 'Original Publication Year'])
    df=df.fillna(-1)
    df.rename(columns= {'Book Id':'goodreads_id', 'Title':'title', 'Author':'author', 'Publisher':'publisher', 'Number of Pages':'number_of_pages', 'Year Published':'year_published', 'Original Publication Year':'original_publication_year'}, inplace = True)
    df = df.astype({'goodreads_id':'string', 'title':'string','author':'string','publisher':'string','number_of_pages':'Int64', 'year_published':'Int64', 'original_publication_year':'Int64'})

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