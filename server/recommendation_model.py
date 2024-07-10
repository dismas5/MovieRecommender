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