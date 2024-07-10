import Foundation

struct Movie: Decodable, Equatable {
    let id: Int
    let title: String
    let genres: String
    let moviesRated: Int
    
    enum CodingKeys: String, CodingKey {
        case id = "movieId"
        case title
        case genres
        case moviesRated = "moviesRated"
    }
}
