import Foundation

protocol NetworkManager: AnyObject {
    init(baseURLString: String)
    
    func fetchNextMovie() async throws -> Movie
    func fetchMovieImageData(for movie: Movie) async throws -> Data
    func fetchRecommendations() async throws -> [String]
    func rate(movie: Movie, rating: Int) async throws
}
