//
//  ViewController.swift
//  MovieRecommender
//
//  Created by Dimasik on 13.06.2024.
//

import UIKit

final class ViewController: UIViewController {
    
    @IBOutlet private var moviePicture: UIImageView!
    @IBOutlet private var movieTitle: UILabel!
    @IBOutlet var ratingsCountLabel: UILabel!
    @IBOutlet var stopRatingButton: UIButton!
    @IBOutlet var movieGenre: UILabel!
    
    private var manager = NetworkManager(link: "http://127.0.0.1:5000");
    
    private let mandatoryRatingAmount = 10
    
    override func viewDidLoad() {
        super.viewDidLoad()
        stopRatingButton.isHidden = true
        pullNextMovie()
    }
    
    private func pullNextMovie() {
        manager.parseNextMovie { [weak self] in
            guard let self = self else { return }
            guard let movieData = self.manager.result else {
                print("Something went wrong.")
                return
            }
            
            movieTitle.text = movieData.title
            movieGenre.text = movieData.genres
        }
    }
    
    @IBAction func rateCurrentMovie(sender: RatingButton) {
        manager.rateCurrentMovie(rating: sender.buttonRating)
        
        pullNextMovie()
    }
}

