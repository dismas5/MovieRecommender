import Foundation

struct IMDBMovie: Decodable {
    var imageURL: URL
    
    enum CodingKeys: String, CodingKey {
        case imageURL = "Poster"
    }
}
