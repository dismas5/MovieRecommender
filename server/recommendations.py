import tensorflow as tf
import pandas as pd
import numpy as np

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
