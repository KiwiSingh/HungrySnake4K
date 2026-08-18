import UIKit

// This file is NOT from DeepSeek — it's a small addition to make the real
// SnakeGame.swift and GameView.swift actually compile.
//
// SnakeGame.swift references `Point.zero`, but Point never defines it.
// GameView.swift references `UIColor.gold`, `UIColor.silver`, and
// `UIColor.darkGreen`, which aren't part of standard UIKit.
// Tweak the exact colors below to taste.

extension Point {
    static let zero = Point(x: 0, y: 0)
}

extension UIColor {
    static let gold = UIColor(red: 1.0, green: 0.84, blue: 0.0, alpha: 1.0)
    static let silver = UIColor(red: 0.75, green: 0.75, blue: 0.75, alpha: 1.0)
    static let darkGreen = UIColor(red: 0.0, green: 0.3, blue: 0.0, alpha: 1.0)
}
