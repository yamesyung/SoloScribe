import pandas as pd
import psycopg2
import sqlalchemy

"""
    scripts used to load data into db before file upload, left for reference
"""

if __name__ == '__main__':

    data = pd.read_csv(r'/home/john/Desktop/library.csv')
    df = pd.DataFrame(data, columns=['Book Id', 'Title', 'Author', 'My Rating','Original Publication Year', 'Date Read', 'Date Added', 'Exclusive Shelf', 'My Review', 'Private Notes', 'Read Count', 'Owned Copies'])
    df = df.fillna(-1)
    df.rename(columns= {'Book Id':'goodreads_id', 'Title':'title', 'Author':'author', 'My Rating':'rating', 'Original Publication Year':'original_publication_year', 'Date Read':'date_read', 'Date Added':'date_added', 'Exclusive Shelf':'bookshelves', 'My Review':'review', 'Private Notes':'private_notes', 'Read Count':'read_count', 'Owned Copies':'owned_copies'}, inplace = True)
    df = df.astype({'goodreads_id':'string', 'title':'string', 'author':'string', 'rating':'Int32', 'original_publication_year':'Int32', 'date_read':'datetime64[ns]', 'date_added':'datetime64[ns]', 'bookshelves':'string', 'review':'string', 'private_notes':'string', 'read_count':'Int32', 'owned_copies':'Int32'})

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
        df.to_sql("books_review", engine, "public", index=False, if_exists='append')
        print('loaded')
    except:
        print('cannot be loaded')

    if conn:
        curr.close()
        conn.close()
        print("PostgreSQL connection is closed")