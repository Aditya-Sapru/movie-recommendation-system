from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from typing import List, Dict

class MovieRecommender:
    def __init__(self):
        self.engine = create_engine('postgresql://postgres:Adianshu00#@localhost:5432/moviedb')
        self.df = pd.read_sql("SELECT * FROM movies", self.engine)
        self.vectorizer = TfidfVectorizer(stop_words='english')
        # Create a combined text field for better matching
        self.df['combined_features'] = self.df['Movie Title'].fillna('') + ' ' + self.df['Description'].fillna('')
        # Fit the vectorizer on all movie data
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['combined_features'])
        
    def get_recommendations_by_keyword(self, keyword: str, num_recommendations: int = 7) -> List[Dict]:
        """
        Get movie recommendations based on keyword search using cosine similarity
        """
        # Transform the keyword using the same vectorizer
        keyword_vector = self.vectorizer.transform([keyword])
        
        # Calculate cosine similarity between keyword and all movies
        cosine_similarities = cosine_similarity(keyword_vector, self.tfidf_matrix).flatten()
        
        # Get indices of top similar movies
        similar_indices = cosine_similarities.argsort()[::-1][:num_recommendations]
        
        # Get the recommended movies
        recommendations = []
        for idx in similar_indices:
            if cosine_similarities[idx] > 0:  # Only include if there's some similarity
                recommendations.append({
                    'movie_id': int(self.df.iloc[idx]['Rank']),
                    'title': self.df.iloc[idx]['Movie Title'],
                    'description': self.df.iloc[idx]['Description'],
                    'similarity_score': float(cosine_similarities[idx]),
                    'genres': 'N/A',  # Since we don't have genre information
                    'rating': 0.0  # Since we don't have rating information
                })
        
        return recommendations

    def get_similar_movies(self, movie_id: int, num_recommendations: int = 7) -> List[Dict]:
        """
        Get similar movies based on a specific movie ID
        """
        movie_idx = self.df[self.df['Rank'] == movie_id].index[0]
        movie_vector = self.tfidf_matrix[movie_idx]
        
        # Calculate cosine similarity between the movie and all other movies
        cosine_similarities = cosine_similarity(movie_vector, self.tfidf_matrix).flatten()
        
        # Get indices of top similar movies (excluding the movie itself)
        similar_indices = cosine_similarities.argsort()[::-1][1:num_recommendations+1]
        
        # Get the recommended movies
        recommendations = []
        for idx in similar_indices:
            recommendations.append({
                'movie_id': int(self.df.iloc[idx]['Rank']),
                'title': self.df.iloc[idx]['Movie Title'],
                'description': self.df.iloc[idx]['Description'],
                'similarity_score': float(cosine_similarities[idx]),
                'genres': 'N/A',  # Since we don't have genre information
                'rating': 0.0  # Since we don't have rating information
            })
        
        return recommendations 