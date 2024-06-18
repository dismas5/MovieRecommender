import SwiftUI

struct MainView: View {
    let viewModel: MainViewModel
    
    var body: some View {
        ZStack {
            VStack(spacing: 12) {
                titleView
                    .foregroundStyle(.ultraThickMaterial)
                    .blendMode(.difference)
                    .padding(.horizontal, 16)
                    .padding(.top, 8)
                
                if let movie = viewModel.movie {
                    movieImageView
                    
                    VStack {
                        movieDetailsView(movie)
                            .padding(.horizontal, 20)
                            .foregroundStyle(.ultraThickMaterial)
                        
                        RatingButtons(action: viewModel.handleRatingTapped)
                            .disabled(viewModel.isLoading)
                            .padding(.horizontal, 24)
                            .padding(.vertical, 10)
                        controlButtons(movie.moviesRated)
                    }
                    .padding(.top, 16)
                    .background {
                        UnevenRoundedRectangle(topLeadingRadius: 36, topTrailingRadius: 36, style: .continuous)
                            .foregroundStyle(.ultraThinMaterial)
                            .ignoresSafeArea()
                    }
                } else {
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            
            if let errorMessage = viewModel.errorMessage {
                errorView(errorMessage)
            }
        }
        .animation(.default, value: viewModel.errorMessage)
        .background {
            Color.black
                .ignoresSafeArea()
            
            backgroundBlurView
        }
        .task {
            await viewModel.fetchMovie()
        }
    }
    
    @MainActor
    @ViewBuilder
    private var titleView: some View {
        Text("Welcome to Movie Recommender")
            .font(.title)
            .fontWeight(.bold)
            .frame(maxWidth: .infinity, alignment: .leading)
    }

    @MainActor
    @ViewBuilder
    private var movieImageView: some View {
        VStack(spacing: 0) {
            Spacer()
            
            ZStack {
                if let image = viewModel.image {
                    Image(uiImage: image)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
                        .id("poster_\(viewModel.movie?.id ?? -1)")
                        .transition(.blurReplace.animation(.default))
                } else {
                    ProgressView()
                }
            }
            .shadow(color: .black.opacity(0.6), radius: 5, y: 3)
            
            Spacer()
        }
    }
    
    @MainActor
    @ViewBuilder
    private func movieDetailsView(_ movie: Movie) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(movie.title)
            
            Text(movie.genres)
                .font(.caption)
                .foregroundStyle(.secondary)
                .padding(.vertical, 2)
                .padding(.horizontal, 6)
                .background {
                    Capsule()
                        .stroke(lineWidth: 1)
                        .foregroundStyle(.secondary)
                }
        }
        .frame(maxWidth: .infinity, minHeight: 80, alignment: .topLeading)
    }
    
    @MainActor
    @ViewBuilder
    private func controlButtons(_ ratingCount: Int) -> some View {
        HStack {
            Button("Haven't seen this movie") {
                viewModel.handleRatingTapped(0)
            }.cornerRadius(20)
            
            Spacer()
            
            Button("Stop rating") {
                
            }
            .disabled(ratingCount <= 10)
            .cornerRadius(20)
            .tint(.black)
        }
        .buttonStyle(.borderedProminent)
        .controlSize(.large)
        .padding(.horizontal, 20)
        .disabled(viewModel.isLoading)
    }
    
    @MainActor
    @ViewBuilder
    private func errorView(_ message: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.title2)
                .foregroundStyle(.red)
            
            Text(message)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .foregroundStyle(.background)
                .shadow(radius: 10)
        }
        .frame(maxHeight: .infinity, alignment: .bottom)
        .transition(.move(edge: .bottom))
        .contentShape(.interaction, Rectangle())
        .onTapGesture {
            viewModel.dismissErrorMessage()
        }
        .zIndex(10)
    }
    
    @MainActor
    @ViewBuilder
    private var backgroundBlurView: some View {
        if let image = viewModel.image {
            Image(uiImage: image)
                .resizable()
                .aspectRatio(contentMode: .fill)
                .ignoresSafeArea()
                .blur(radius: 100)
                .brightness(-0.1)
                .id("background_\(viewModel.movie?.id ?? -1)")
                .transition(.opacity.animation(.default.speed(0.5)))
        }
    }
}

#if DEBUG
#Preview {
    MainView(viewModel: MainViewModel(networkManager: .preview))
}
#endif
