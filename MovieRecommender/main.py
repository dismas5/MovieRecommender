import random
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from sklearn.metrics.pairwise import cosine_similarity
import re
import tensorflow as tf

class RecommenderNet(tf.keras.Model):
    def __init__(self, num_users, num_movies, embedding_size, **kwargs):
        super(RecommenderNet, self).__init__(**kwargs)
        self.num_users = num_users
        self.num_movies = num_movies
        self.user_embedding = tf.keras.layers.Embedding(num_users + 1, embedding_size, embeddings_initializer='he_normal')
        self.user_bias = tf.keras.layers.Embedding(num_users + 1, 1)
        self.movie_embedding = tf.keras.layers.Embedding(num_movies + 1, embedding_size, embeddings_initializer='he_normal')
        self.movie_bias = tf.keras.layers.Embedding(num_movies + 1, 1)
    
    def call(self, inputs):
        user_vector = self.user_embedding(inputs[:, 0])
        user_bias = self.user_bias(inputs[:, 0])
        movie_vector = self.movie_embedding(inputs[:, 1])
        movie_bias = self.movie_bias(inputs[:, 1])
        
        dot_user_movie = tf.tensordot(user_vector, movie_vector, 2)
        
        x = dot_user_movie + user_bias + movie_bias
        
        return tf.nn.sigmoid(x)

app = Flask(__name__)

model = tf.keras.models.load_model('recommendation_model', custom_objects={'RecommenderNet': RecommenderNet})

data = pd.read_csv('ml-100k/u.data', sep='\t', names=['user_id', 'movie_id', 'rating', 'timestamp'])
movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', header=None,
                     names=['movie_id', 'title', 'release_date', 'video_release_date', 'IMDb_URL', 
                            'unknown', 'Action', 'Adventure', 'Animation', 'Children\'s', 'Comedy', 
                            'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 
                            'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'])

# Combine genres for each movie
movies['genres'] = movies[['Action', 'Adventure', 'Animation', 'Children\'s', 'Comedy', 'Crime',
                           'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical',
                           'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']].apply(
                           lambda row: ', '.join(row.index[row == 1]), axis=1)

movies = movies[['movie_id', 'title', 'genres']]
data = pd.merge(data, movies[['movie_id', 'title']], on='movie_id')
data['user_id'] = data['user_id'].astype('category').cat.codes.values
data['movie_id'] = data['movie_id'].astype('category').cat.codes.values
data['rating'] = data['rating'] / 5.0  # Normalize ratings

# Encode genres for embeddings
genre_encoding = pd.get_dummies(movies['genres'])
movies = movies.join(genre_encoding)
movie_embeddings = movies.set_index('movie_id')[genre_encoding.columns].values

# user_ratings = {}
user_ratings = {
  "13": 5,
  "25": 4,
  "26": 5,
  "124": 2,
  "1668": 5
}

unseen_movies = []

def add_new_user_preferences(data, new_user_preferences, movie_titles):
    new_user_ratings = pd.DataFrame(new_user_preferences)
    new_user_ratings['user_id'] = data['user_id'].max() + 1
    new_user_ratings['rating'] = new_user_ratings['rating'] / 5.0
    new_user_ratings = new_user_ratings[['user_id', 'movie_id', 'rating']]
    augmented_data = pd.concat([data, new_user_ratings], ignore_index=True)
    return augmented_data, new_user_ratings['user_id'].iloc[0]

# Function to recommend movies
def recommend_movies(model, data, new_user_preferences, movie_titles, top_k=5, retrain_epochs=6):
    augmented_data, new_user_id = add_new_user_preferences(data, new_user_preferences, movie_titles)
    train_data = tf.data.Dataset.from_tensor_slices((augmented_data[['user_id', 'movie_id']].values.astype(np.int16), augmented_data['rating'].values))
    batch_size = 64
    train_data = train_data.shuffle(len(augmented_data)).batch(batch_size)
    
    # Define a new optimizer with a possibly different learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss=tf.keras.losses.BinaryCrossentropy()
    )

    model.fit(train_data, epochs=retrain_epochs, verbose=1)
    
    all_movies = movie_titles['movie_id'].values
    user_movie_array = np.hstack((np.array([new_user_id] * len(all_movies)).reshape(-1, 1), all_movies.reshape(-1, 1))).astype(np.int16)
    
    predictions = model.predict(user_movie_array).flatten()
    top_indices = predictions.argsort()[-top_k:][::-1]
    recommended_movie_ids = all_movies[top_indices]
    recommended_movies = movie_titles[movie_titles['movie_id'].isin(recommended_movie_ids)]
    return recommended_movies['title'].values

def remove_year(movie_title):
    pattern = r'\s*\(\d{4}\)$'
    return re.sub(pattern, '', movie_title)

def recommend_movie(user_ratings, movie_embeddings, epsilon=0.1, exploration_rate=0.2):
    rated_movies = list(user_ratings.keys())
    unrated_movies = [movie for movie in range(len(movie_embeddings)) if movie + 1 not in rated_movies and movie + 1 not in unseen_movies]

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
                           if any(genre in movies.loc[movies['movie_id'] == movie_id + 1, 'genres'].values[0].split(', ')
                                  for genre in unrated_genres)]

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


@app.route('/get_recommendation', methods=['GET'])
def get_recommendation():
    preferences = [ {'movie_id': id, 'rating': rating } for id, rating in user_ratings.items()]
    recommended_movies = recommend_movies(model, data, preferences, movies[['movie_id', 'title']])
    return jsonify(recommended_movies.tolist())

@app.route('/next_movie', methods=['GET'])
def get_next_movie():
    movie_id = recommend_movie(user_ratings, movie_embeddings, epsilon=0.05, exploration_rate=0.2)
    movie_details = movies[movies['movie_id'] == movie_id][['movie_id', 'title', 'genres']].to_dict(orient='records')[0]
    movie_details['title'] = remove_year(movie_details['title'])
    movie_details['movies_rated'] = len(user_ratings)
    return jsonify(movie_details)

@app.route('/get_movies_by_genre', methods=['GET'])
def get_movies_by_genre(genre: str = "Animation"):
    movie_details = movies[movies['genres'].str.contains(genre)][['movie_id', 'title', 'genres']].to_dict(orient='records')
    return jsonify(movie_details)

@app.route('/all_movies', methods=['GET'])
def get_all_movies():
    return jsonify(movies[['movie_id', 'title', 'genres']].to_dict(orient='records'))

@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    data = request.json
    movie_id = data['movie_id']
    rating = data['rating']
    
    if rating == 0:
        unseen_movies.append(movie_id)
    else:
        user_ratings[movie_id] = rating
    return jsonify({'message': 'Rating received'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)
