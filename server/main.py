import pandas as pd
import re

from tensorflow.keras.models import load_model
from flask import Flask, request, jsonify

from paths import *
from recommendations import recommend_new_movies, recommend_movie_for_rating
from recommendation_model import RecommenderNet
from user_rating import UserRating

app = Flask(__name__)

model = load_model(RECOMMENDATION_MODEL_PATH, custom_objects={'RecommenderNet': RecommenderNet})

genres_list = pd.read_csv(DATASET_FOLDER_PATH + '/u.genre', sep='|', names=['genres', 'id'])
genres_list = genres_list['genres'].to_list()
data = pd.read_csv(DATASET_FOLDER_PATH + '/u.data', sep='\t', names=['user_id', 'movie_id', 'rating', 'timestamp'])
movies = pd.read_csv(DATASET_FOLDER_PATH + '/u.item', sep='|', encoding='latin-1', header=None,
                     names=['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL'] + genres_list)

# Combine genres for each movie
movies['genres'] = movies[genres_list].apply(lambda row: ', '.join(row.index[row == 1]), axis=1)

movies = movies[['movie_id', 'title', 'genres']]
data = pd.merge(data, movies[['movie_id', 'title']], on='movie_id')
data['user_id'] = data['user_id'].astype('category').cat.codes.values
data['movie_id'] = data['movie_id'].astype('category').cat.codes.values
data['rating'] = data['rating'] / 5.0

# Encode genres for embeddings
genre_encoding = pd.get_dummies(movies['genres'])
movies = movies.join(genre_encoding)
movie_embeddings = movies.set_index('movie_id')[genre_encoding.columns].values

ratings = UserRating()

def remove_year(movie_title):
    pattern = r'\s*\(\d{4}\)$'
    return re.sub(pattern, '', movie_title)


@app.route('/get_recommendation')
def get_recommendation():
    preferences = [ {'movie_id': id, 'rating': rating } for id, rating in ratings.data()]
    recommended_movies = recommend_new_movies(model, data, preferences, movies[['movie_id', 'title']])
    return jsonify(recommended_movies.tolist())

@app.route('/next_movie')
def get_next_movie():
    movie_id = recommend_movie_for_rating(movies, ratings, movie_embeddings, genre_encoding, epsilon=0.05, exploration_rate=0.2)
    movie_details = movies[movies['movie_id'] == movie_id][['movie_id', 'title', 'genres']].to_dict(orient='records')[0]
    movie_details['title'] = remove_year(movie_details['title'])
    movie_details['movies_rated'] = len(ratings)
    return jsonify(movie_details)

@app.route('/get_movies_by_genre')
def get_movies_by_genre(genre: str = "Animation"):
    movie_details = movies[movies['genres'].str.contains(genre)][['movie_id', 'title', 'genres']].to_dict(orient='records')
    return jsonify(movie_details)

@app.route('/all_movies')
def get_all_movies():
    return jsonify(movies[['movie_id', 'title', 'genres']].to_dict(orient='records'))

@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    data = request.json
    movie_id = data['movie_id']
    rating = data['rating']
    
    ratings.append(movie_id, rating)
    return jsonify({'message': 'Rating received'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)
