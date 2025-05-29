import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import ast

# Load and preprocess dataset once
def load_and_prepare_data(sample_size=5000):
    df = pd.read_csv("movies_metadata.csv", low_memory=False)
    df = df[df['overview'].notna() & df['title'].notna()]
    df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)

    def parse_genres(genre_str):
        try:
            genres = ast.literal_eval(genre_str)
            return " ".join([g['name'] for g in genres]) if isinstance(genres, list) else ""
        except Exception:
            return ""

    df['genres'] = df['genres'].fillna('').apply(parse_genres)
    df['tagline'] = df['tagline'].fillna('')
    df['combined_features'] = df['genres'] + " " + df['overview'] + " " + df['tagline']
    return df

# Pre-load once to avoid repeating at each request
df = load_and_prepare_data()
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['combined_features'])

# Core function to get recommendations
def get_recommendations_by_keyword(keyword, num_results=10):
    if not keyword:
        return []

    keyword_vec = tfidf.transform([keyword])
    cosine_sim = linear_kernel(keyword_vec, tfidf_matrix).flatten()
    sim_scores = list(enumerate(cosine_sim))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[:num_results]
    movie_indices = [i[0] for i in sim_scores]
    return df[['title', 'genres', 'vote_average']].iloc[movie_indices].to_dict(orient='records')
