import SwiftUI

@main
struct MovieRecommenderApp: App {
    let viewModel = MainViewModel(networkManager: .live("http://127.0.0.1:5000"))
//    let viewModel = MainViewModel(networkManager: .preview)
    
    var body: some Scene {
        WindowGroup {
            MainView(viewModel: viewModel)
        }
    }
}
