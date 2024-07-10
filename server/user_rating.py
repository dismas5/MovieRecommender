class UserRating:
    def __init__(self):
        self.ratings = {}
        self.unseen_movies = []

    def data(self):
        return self.ratings.items()
    
    def __len__(self):
        return len(self.ratings)
    
    def rated_movies(self):
        return self.ratings.keys()

    def append(self, movie_id, rating):
        if rating == 0:
            self.unseen_movies.append(movie_id)
        else:
            self.ratings[movie_id] = rating