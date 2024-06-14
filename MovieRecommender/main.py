from flask import Flask, request, jsonify
import random
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

ratings = pd.read_csv('ml-100k/u.data', sep='\t', names=['user_id', 'movie_id', 'rating', 'timestamp'])
movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', header=None,
                     names=['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL', 
                            'unknown', 'Action', 'Adventure', 'Animation', 'Children\'s', 'Comedy', 
                            'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 
                            'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'])

movies = movies[['movie_id', 'title', 'Action', 'Adventure', 'Animation', 'Children\'s', 'Comedy',
                 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical',
                 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']]

genre_cols = ['Action', 'Adventure', 'Animation', 'Children\'s', 'Comedy', 'Crime', 'Documentary', 'Drama',
              'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 
              'War', 'Western']
movies['genres'] = movies[genre_cols].idxmax(axis=1)
movies = movies.drop(columns=genre_cols)
data = pd.merge(ratings, movies, on='movie_id')

genre_encoding = pd.get_dummies(movies['genres'])
movies = movies.join(genre_encoding)
movie_embeddings = movies.set_index('movie_id')[genre_encoding.columns].values

user_ratings = {}

def recommend_movie(user_ratings, movie_embeddings, epsilon=0.1, exploration_rate=0.2):
    rated_movies = list(user_ratings.keys())
    unrated_movies = [movie for movie in range(len(movie_embeddings)) if movie + 1 not in rated_movies]

    if not rated_movies:
        return random.choice(unrated_movies) + 1

    rated_genres = set(movies.loc[movies['movie_id'].isin(rated_movies), 'genres'])
    all_genres = set(movies['genres'])
    unrated_genres = all_genres - rated_genres

    rated_embeddings = np.array([movie_embeddings[movie - 1] for movie in rated_movies])
    mean_embedding = np.mean(rated_embeddings, axis=0).reshape(1, -1)
    similarities = cosine_similarity(mean_embedding, movie_embeddings[unrated_movies])
    similarity_scores = similarities.flatten()

    for movie_id, rating in user_ratings.items():
        genre = movies.loc[movies['movie_id'] == movie_id, 'genres'].values[0]
        genre_col = genre_encoding.columns.get_loc(genre)
        if rating <= 2:
            genre_adjustment = movie_embeddings[unrated_movies, genre_col]
            similarity_scores -= genre_adjustment * (3 - rating)

    exploration_indices = [i for i, movie_id in enumerate(unrated_movies)
                           if movies.loc[movies['movie_id'] == movie_id + 1, 'genres'].values[0] in unrated_genres]

    if random.random() < epsilon:
        if exploration_indices and random.random() < exploration_rate:
            next_movie = unrated_movies[random.choice(exploration_indices)]
        else:
            next_movie = random.choice(unrated_movies)
    else:
        if exploration_indices and random.random() < exploration_rate:
            next_movie = unrated_movies[random.choice(exploration_indices)]
        else:
            next_movie = unrated_movies[np.argmax(similarity_scores)]
    
    return next_movie + 1

@app.route('/next_movie', methods=['GET'])
def get_next_movie():
    movie_id = recommend_movie(user_ratings, movie_embeddings, epsilon=0.05, exploration_rate=0.2)
    movie_details = movies[movies['movie_id'] == movie_id][['movie_id', 'title', 'genres']].to_dict(orient='records')[0]
    return jsonify(movie_details)

@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    data = request.json
    movie_id = data['movie_id']
    rating = data['rating']
    user_ratings[movie_id] = rating
    return jsonify({'message': 'Rating received'}), 200

if __name__ == '__main__':
    app.run(debug=True)
