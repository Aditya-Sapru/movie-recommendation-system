from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from movie_recommender import MovieRecommender

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the recommender
recommender = MovieRecommender()

class MovieResponse(BaseModel):
    movie_id: int
    title: str
    description: str
    similarity_score: float
    genres: str
    rating: float

@app.get("/")
async def read_root():
    return {"message": "Movie Recommendation API is running"}

@app.get("/search/{keyword}", response_model=List[MovieResponse])
async def search_movies(keyword: str, limit: Optional[int] = 7):
    try:
        recommendations = recommender.get_recommendations_by_keyword(keyword, limit)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/similar/{movie_id}", response_model=List[MovieResponse])
async def get_similar_movies(movie_id: int, limit: Optional[int] = 7):
    try:
        recommendations = recommender.get_similar_movies(movie_id, limit)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))