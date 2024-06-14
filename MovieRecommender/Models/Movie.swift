//
//  Movie.swift
//  MovieRecommender
//
//  Created by Dimasik on 14.06.2024.
//

import Foundation

struct Movie: Decodable {
    let genres: String
    let movie_id: Int
    let title: String
}
