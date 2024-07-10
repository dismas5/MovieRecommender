import tensorflow as tf
import pandas as pd
import numpy as np
import random

from sklearn.metrics.pairwise import cosine_similarity

from user_rating import UserRating

def add_new_user_preferences(data, new_user_preferences):
    new_user_ratings = pd.DataFrame(new_user_preferences)
    new_user_ratings['user_id'] = data['user_id'].max() + 1
    new_user_ratings['rating'] = new_user_ratings['rating'] / 5.0
    new_user_ratings = new_user_ratings[['user_id', 'movie_id', 'rating']]
    augmented_data = pd.concat([data, new_user_ratings], ignore_index=True)
    return augmented_data, new_user_ratings['user_id'].iloc[0]

def recommend_new_movies(model, data, new_user_preferences, movie_titles, top_k=5, retrain_epochs=6):
    augmented_data, new_user_id = add_new_user_preferences(data, new_user_preferences)
    train_data = tf.data.Dataset.from_tensor_slices((augmented_data[['user_id', 'movie_id']].values.astype(np.int16), augmented_data['rating'].values))
    batch_size = 64
    train_data = train_data.shuffle(len(augmented_data)).batch(batch_size)
    
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

def recommend_movie_for_rating(movies: pd.DataFrame, ratings: UserRating, movie_embeddings, genre_encoding, epsilon=0.1, exploration_rate=0.2):
    rated_movies = ratings.rated_movies()
    unrated_movies = [movie for movie in range(len(movie_embeddings)) if movie + 1 not in rated_movies and movie + 1 not in ratings.unseen_movies]

    if not rated_movies:
        return random.choice(unrated_movies) + 1

    rated_genres = set(movies.loc[movies['movie_id'].isin(rated_movies), 'genres'])
    all_genres = set(movies['genres'])
    unrated_genres = all_genres - rated_genres

    rated_embeddings = np.array([movie_embeddings[movie - 1] for movie in rated_movies])
    mean_embedding = np.mean(rated_embeddings, axis=0).reshape(1, -1)
    similarities = cosine_similarity(mean_embedding, movie_embeddings[unrated_movies])
    similarity_scores = similarities.flatten()

    for movie_id, rating in ratings.items():
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