import Foundation

final class PreviewNetworkManager: NetworkManager {
    private let movies = [
        Movie(id: 1, title: "The Shawshank Redemption", genres: "Drama", moviesRated: 0),
        Movie(id: 2, title: "The Godfather", genres: "Crime", moviesRated: 0),
        Movie(id: 3, title: "The Dark Knight", genres: "Action", moviesRated: 0),
        Movie(id: 4, title: "12 Angry Men", genres: "Crime", moviesRated: 0),
        Movie(id: 5, title: "Schindler's List", genres: "Biography", moviesRated: 0),
        Movie(id: 6, title: "Pulp Fiction", genres: "Crime", moviesRated: 0),
        Movie(id: 7, title: "The Lord of the Rings: The Fellowship of the Ring", genres: "Adventure", moviesRated: 0),
        Movie(id: 8, title: "Forrest Gump", genres: "Romance", moviesRated: 0),
        Movie(id: 9, title: "Fight Club", genres: "Drama", moviesRated: 0),
        Movie(id: 10, title: "Inception", genres: "Sci-Fi", moviesRated: 0),
        Movie(id: 11, title: "The Matrix", genres: "Sci-Fi", moviesRated: 0),
        Movie(id: 12, title: "One Flew Over the Cuckoo's Nest", genres: "Drama", moviesRated: 0),
        Movie(id: 13, title: "Seven", genres: "Mystery", moviesRated: 0),
        Movie(id: 14, title: "Interstellar", genres: "Sci-Fi", moviesRated: 0),
        Movie(id: 15, title: "Seven Samurai", genres: "Drama", moviesRated: 0)
    ]
    
    init(baseURLString: String) {
    }
    
    func fetchNextMovie() async throws -> Movie {
        movies.randomElement()!
    }
    
    func fetchMovieImageData(for movie: Movie) async throws -> Data {
        try await LiveNetworkManager(baseURLString: "http://127.0.0.1:5000").fetchMovieImageData(for: movie)
    }
    
    func rate(movie: Movie, rating: Int) async throws {
    }
    
    func fetchRecommendations() async throws -> Array<String> {
        [
            "Movie recommendation 1",
            "Movie recommendation 2",
            "Movie recommendation 3",
            "Movie recommendation 4",
            "Movie recommendation 5",
            "Movie recommendation 6",
            "Movie recommendation 7",
            "Movie recommendation 8",
            "Movie recommendation 9",
            "Movie recommendation 10",
        ]
    }
}

// MARK: Protocol access
extension NetworkManager where Self == PreviewNetworkManager {
    static var preview: Self {
        PreviewNetworkManager(baseURLString: "")
    }
}
