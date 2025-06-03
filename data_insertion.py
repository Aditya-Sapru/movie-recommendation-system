from sqlalchemy import create_engine
import pandas as pd

df = pd.read_csv("movies.csv")
engine = create_engine('postgresql://postgres:Adianshu00#@localhost:5432/moviedb')
df.to_sql('movies', engine, if_exists='replace', index=False)
