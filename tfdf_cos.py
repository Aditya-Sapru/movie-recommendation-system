from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine

import pandas as pd

engine = create_engine('postgresql://postgres:Adianshu00#@localhost:5432/moviedb')
# Assuming your df has a 'description' or 'genres' field
df = pd.read_sql("SELECT * FROM movies", engine)
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['Movie Title'] + " " + df['Description'])  # or description
cos_sim = cosine_similarity(tfidf_matrix)

# Save similarity matrix for use in recommendations
import numpy as np
np.save('cosine_sim.npy', cos_sim)
