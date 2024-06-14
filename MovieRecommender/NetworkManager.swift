//
//  DataParser.swift
//  MovieRecommender
//
//  Created by Dimasik on 13.06.2024.
//

import Foundation

class NetworkManager {
    
    init(link: String) {
        nextMovieUrl = URL(string: link + "/next_movie")!
        rateMovieUrl = URL(string: link + "/rate_movie")!
    }
    
    private var rateMovieUrl: URL
    private var nextMovieUrl: URL
    var result: Movie? = nil
    
    func parseNextMovie(completion: @escaping () -> Void) {
        URLSession.shared.dataTask(with: nextMovieUrl) { data, _, error in
            guard let data = data, error == nil else {
                print("Error fetching next movie: \(String(describing: error))")
                return
            }
            
            do {
                self.result = try JSONDecoder().decode(Movie.self, from: data)
                
                DispatchQueue.main.async {
                    completion()
                }
            } catch {
                print("Error: \(error)")
            }
            return
        }.resume()
    }
    
    func rateCurrentMovie(rating: Int/*, completion: @escaping () -> Void*/) {
        guard let movieId = result?.movie_id else { return }
        
        var request = URLRequest(url: rateMovieUrl)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let ratingData = Rating(movie_id: movieId, rating: rating)
        request.httpBody = try? JSONEncoder().encode(ratingData)
        
        URLSession.shared.dataTask(with: request) { _, _, error in
            if error == nil {
                print("Error sending rating: \(String(describing: error))")
                return
            }
            
//            DispatchQueue.main.async {
//                completion()
//            }
        }.resume()
    }
}
