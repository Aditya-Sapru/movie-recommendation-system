Movie Recommendendation System

This system is based on the IMDBs top 250 movies chart(https://www.imdb.com/chart/top/)
The data is stored in a movie table in a dataset in PostgresSQL
Pythons scikit-learn library used to vectorize the movie title and description columns to get a matrix. After the user enters a keywrd that keyword is vetorized an a cosine similarity operation is applied.
A similar function called "get similar movies" uses a similar logic to find movies based on the movie id.
Utilizes Tailwind CSS for UI
