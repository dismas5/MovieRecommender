import SwiftUI

struct RatingButtons: View {
    let action: @MainActor (Rating) -> Void
    
    var body: some View {
        HStack {
            ForEach(Rating.allCases, id: \.self) { rating in
                Button(title(for: rating)) {
                    action(rating)
                }
                .font(.title)
                .buttonStyle(.rating(rating))
                .frame(maxWidth: .infinity)
            }
        }
    }
    
    private func title(for rating: Rating) -> String {
        switch rating {
        case .veryBad: "☹️"
        case .bad: "😕"
        case .neutral: "😐"
        case .good: "🙂"
        case .veryGood: "😀"
        }
    }
}

// MARK: Button style
struct RatingButtonStyle: ButtonStyle {
    let rating: Rating
    
    private var color: Color {
        switch rating {
        case .veryBad: .Colors.veryBad
        case .bad: .Colors.bad
        case .neutral: .Colors.neutral
        case .good: .Colors.good
        case .veryGood: .Colors.veryGood
        }
    }
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .frame(maxWidth: .infinity)
            .aspectRatio(1, contentMode: .fit)
            .frame(width: 60, height: 60)
            .background {
                Circle()
                    .shadow(color: .black.opacity(0.3), radius: 3)
                    .foregroundStyle(.ultraThinMaterial)
                    .colorMultiply(color)
            }
            .scaleEffect(configuration.isPressed ? 0.8 : 1.0)
    }
}

// MARK: Protocol access
extension ButtonStyle where Self == RatingButtonStyle {
    static func rating(_ rating: Rating) -> Self {
        RatingButtonStyle(rating: rating)
    }
}

#if DEBUG
#Preview("Rate buttons") {
    RatingButtons { _ in }
}
#endif
