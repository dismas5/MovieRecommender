import Foundation

final class LiveNetworkManager: NetworkManager {
    private let baseURL: URL
    private let urlSession = URLSession.shared
    private let decoder = {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return decoder
    }()
    
    init(baseURLString: String) {
        baseURL = URL(string: baseURLString)!
    }
    
    func fetchNextMovie() async throws -> Movie {
        do {
            let url = baseURL.appending(path: Endpoints.nextMovie.rawValue)
            let (data, _) = try await urlSession.data(from: url)
            
            let movie = try decoder.decode(Movie.self, from: data)
            return movie
        } catch {
            throw Error.failedToFetchMovie(underlyingError: error)
        }
    }
    
    func fetchMovieImageData(for movie: Movie) async throws -> Data {
        do {
            let imdbMovie = try await fetchIMDBMovie(movie)
            let (data, _) = try await urlSession.data(from: imdbMovie.imageURL)
            return data
        } catch {
            throw Error.failedToFetchIMDBImageData(underlyingError: error)
        }
    }
    
    func rate(movie: Movie, rating: Int) async throws {
        do {
            var request = URLRequest(url: baseURL.appending(path: Endpoints.rateMovie.rawValue))
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            let rating = MovieRating(movieId: movie.id, rating: rating)
            let encoder = JSONEncoder()
            encoder.keyEncodingStrategy = .convertToSnakeCase
            request.httpBody = try encoder.encode(rating)
            
            _ = try await urlSession.data(for: request)
        } catch {
            throw Error.failedToPostRating(underlyingError: error)
        }
    }
    
    private func fetchIMDBMovie(_ movie: Movie) async throws -> IMDBMovie {
        var urlComponents = URLComponents(string: Endpoints.imdb.rawValue)
        urlComponents?.queryItems = [
            URLQueryItem(name: "t", value: movie.title),
            URLQueryItem(name: "apikey", value: Tokens.imdbToken)
        ]
        
        guard let url = urlComponents?.url else {
            throw Error.failedToCreateIMDBURL
        }
        
        let (data, _) = try await urlSession.data(from: url)
        let imdbMovie = try decoder.decode(IMDBMovie.self, from: data)
        return imdbMovie
    }
}

// MARK: Protocol access
extension NetworkManager where Self == LiveNetworkManager {
    static func live(_ baseURLString: String) -> Self {
        LiveNetworkManager(baseURLString: baseURLString)
    }
}

// MARK: Endpoints
extension LiveNetworkManager {
    enum Endpoints: String {
        case nextMovie = "next_movie"
        case rateMovie = "rate_movie"
        case imdb = "http://www.omdbapi.com/?i=tt3896198&apikey=e21fc0f7"
    }
}

// MARK: Tokens
extension LiveNetworkManager {
    enum Tokens {
        static let imdbToken = "e21fc0f7"
    }
}

// MARK: Errors
extension LiveNetworkManager {
    enum Error: LocalizedError {
        case failedToFetchMovie(underlyingError: Swift.Error)
        case failedToPostRating(underlyingError: Swift.Error)
        case failedToFetchIMDBImageData(underlyingError: Swift.Error)
        case failedToCreateIMDBURL
        
        var errorDescription: String? {
            switch self {
            case let .failedToFetchMovie(underlyingError):
                "Failed to fetch a new movie. Undelying error: \(underlyingError.localizedDescription)."
            case let .failedToPostRating(underlyingError):
                "Failed to post a rating for a movie. Undelying error: \(underlyingError.localizedDescription)."
            case let .failedToFetchIMDBImageData(underlyingError):
                "Failed to fetch an image data from IMDB. Undelying error: \(underlyingError.localizedDescription)."
            case .failedToCreateIMDBURL:
                "Failed to create a URL for IMDB API."
            }
        }
    }
}
