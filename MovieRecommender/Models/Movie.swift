import Foundation

struct Movie: Decodable, Equatable {
    let id: Int
    let title: String
    let genres: String
    
    enum CodingKeys: String, CodingKey {
        case id = "movieId"
        case title
        case genres
    }
}
