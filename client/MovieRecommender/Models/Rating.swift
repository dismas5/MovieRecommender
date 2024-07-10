
enum Rating: CaseIterable {
    case veryBad
    case bad
    case neutral
    case good
    case veryGood
    
    var value: Int {
        switch self {
        case .veryBad: 1
        case .bad: 2
        case .neutral: 3
        case .good: 4
        case .veryGood: 5
        }
    }
}
