import SwiftUI

@Observable
final class MainViewModel {
    @ObservationIgnored
    private let networkManager: NetworkManager
    
    private(set) var isLoading = false
    private(set) var movie: Movie?
    private(set) var image: UIImage?
    private(set) var errorMessage: String?
    
    init(networkManager: NetworkManager) {
        self.networkManager = networkManager
    }
    
    @MainActor
    func fetchMovie() async {
        isLoading = true
        do {
            let movie = try await networkManager.fetchNextMovie()
            self.movie = movie
            
            let imageData = try await networkManager.fetchMovieImageData(for: movie)
            image = UIImage(data: imageData)
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
    
    @MainActor
    func handleRatingTapped(_ rating: Rating) {
        handleRatingTapped(rating.value)
    }
    
    @MainActor
    func handleRatingTapped(_ rating: Int)
    {
        isLoading = true
        Task { [weak self] in
            defer {
                isLoading = false
            }
            
            guard let self, let movie = movie else { return }
            
            do {
                try await networkManager.rate(movie: movie, rating: rating)
                await fetchMovie()
            } catch {
                errorMessage = error.localizedDescription
            }
        }
    }
    
    @MainActor
    func dismissErrorMessage() {
        errorMessage = nil
    }
}
