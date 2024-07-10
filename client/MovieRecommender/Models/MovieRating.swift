import Foundation

struct MovieRating: Encodable {
    let movieId: Int
    let rating: Int
    
    enum CodingKeys: String, CodingKey {
        case movieId
        case rating
    }
}
