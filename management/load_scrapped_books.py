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
    df_final = pd.json_normalize(df_inter['json_element'].apply(json.loads))
