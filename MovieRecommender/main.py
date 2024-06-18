import pandas as pd
import numpy as np
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

# Load the model
model = tf.keras.models.load_model('recommendation_model', custom_objects={'RecommenderNet': RecommenderNet})

# Reload the original dataset and movie titles
column_names = ['user_id', 'movie_id', 'rating', 'timestamp']
data = pd.read_csv('ml-100k/u.data', sep='\t', names=column_names)
movie_titles = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', usecols=[0, 1], names=['movie_id', 'title'])

data = pd.merge(data, movie_titles, on='movie_id')
data['user_id'] = data['user_id'].astype('category').cat.codes.values
data['movie_id'] = data['movie_id'].astype('category').cat.codes.values
data['rating'] = data['rating'] / 5.0  # Normalize ratings

# Function to add new user preferences and retrain the model temporarily
def add_new_user_preferences(data, new_user_preferences, movie_titles):
    new_user_ratings = pd.DataFrame(new_user_preferences)
    movie_to_id = {v: k for k, v in movie_titles[['movie_id', 'title']].to_dict('split')['data']}
    new_user_ratings['movie_id'] = new_user_ratings['movie_title'].map(movie_to_id)
    new_user_ratings['user_id'] = data['user_id'].max() + 1
    new_user_ratings['rating'] = new_user_ratings['user_rating'] / 5.0
    new_user_ratings = new_user_ratings[['user_id', 'movie_id', 'rating']]
    augmented_data = pd.concat([data, new_user_ratings], ignore_index=True)
    return augmented_data, new_user_ratings['user_id'].iloc[0]

# Function to recommend movies
def recommend_movies(model, data, new_user_preferences, movie_titles, top_k=10, retrain_epochs=5):
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

# Example usage
# new_user_preferences = [
#     {"movie_title": "Lion King, The (1994)", "user_rating": 5.0},
#     {"movie_title": "Akira (1988)", "user_rating": 5.0},
#     {"movie_title": "Cinderella (1950)", "user_rating": 4.0},
#     {"movie_title": "Aladdin and the King of Thieves (1996)", "user_rating": 4.0},
#     {"movie_title": "Dumbo (1941)", "user_rating": 4.0}
# ]

new_user_preferences = [
    {"movie_title": "Star Wars (1977)", "user_rating": 5.0},
    {"movie_title": "Stargate (1994)", "user_rating": 5.0},
    {"movie_title": "Robert A. Heinlein's The Puppet Masters (1994)", "user_rating": 4.0},
    {"movie_title": "Jurassic Park (1993)", "user_rating": 4.0},
    {"movie_title": "Twelve Monkeys (1995)", "user_rating": 4.0},
    {"movie_title": "Terminator 2: Judgment Day (1991)", "user_rating": 4.0}
]

recommendations = recommend_movies(model, data, new_user_preferences, movie_titles)
print(recommendations)

