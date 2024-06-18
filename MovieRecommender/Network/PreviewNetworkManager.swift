import Foundation

final class PreviewNetworkManager: NetworkManager {
    private let movies = [
        Movie(id: 1, title: "The Shawshank Redemption", genres: "Drama"),
        Movie(id: 2, title: "The Godfather", genres: "Crime"),
        Movie(id: 3, title: "The Dark Knight", genres: "Action"),
        Movie(id: 4, title: "12 Angry Men", genres: "Crime"),
        Movie(id: 5, title: "Schindler's List", genres: "Biography"),
        Movie(id: 6, title: "Pulp Fiction", genres: "Crime"),
        Movie(id: 7, title: "The Lord of the Rings: The Fellowship of the Ring", genres: "Adventure"),
        Movie(id: 8, title: "Forrest Gump", genres: "Romance"),
        Movie(id: 9, title: "Fight Club", genres: "Drama"),
        Movie(id: 10, title: "Inception", genres: "Sci-Fi"),
        Movie(id: 11, title: "The Matrix", genres: "Sci-Fi"),
        Movie(id: 12, title: "One Flew Over the Cuckoo's Nest", genres: "Drama"),
        Movie(id: 13, title: "Seven", genres: "Mystery"),
        Movie(id: 14, title: "Interstellar", genres: "Sci-Fi"),
        Movie(id: 15, title: "Seven Samurai", genres: "Drama")
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
}

// MARK: Protocol access
extension NetworkManager where Self == PreviewNetworkManager {
    static var preview: Self {
        PreviewNetworkManager(baseURLString: "")
    }
}
