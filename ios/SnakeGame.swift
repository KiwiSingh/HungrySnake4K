import UIKit

enum Direction {
    case up, down, left, right
    func isOpposite(to other: Direction) -> Bool {
        return (self == .up && other == .down) ||
               (self == .down && other == .up) ||
               (self == .left && other == .right) ||
               (self == .right && other == .left)
    }
}

enum GameState {
    case menu, playing, gameOver
}

struct Point {
    var x: CGFloat
    var y: CGFloat
}

class SnakeGame {
    private let gridWidth: Int
    private let gridHeight: Int
    private let gridSize: CGFloat
    private(set) var snake: [Point] = []
    private(set) var snakeDirection: Direction = .right
    private var nextDirection: Direction = .right
    private(set) var foodPosition: Point = .zero
    private(set) var foodColor: UIColor = .red
    private(set) var score: Int = 0
    private(set) var level: Int = 1
    private(set) var state: GameState = .menu
    private(set) var currentBackground: UIImage? = nil
    private var backgroundImages: [UIImage] = []
    private var moveTimer: TimeInterval = 0
    private let moveInterval: TimeInterval = 0.08 // 12.5 FPS – can be tuned

    init(gridWidth: Int, gridHeight: Int, gridSize: CGFloat) {
        self.gridWidth = gridWidth
        self.gridHeight = gridHeight
        self.gridSize = gridSize
        loadBackgrounds()
        resetToMenu()
    }

    private func loadBackgrounds() {
        for i in 1...10 {
            if let img = UIImage(named: "background_\(String(format: "%02d", i))") {
                backgroundImages.append(img)
            }
        }
    }

    func resetToMenu() {
        state = .menu
        score = 0
        level = 1
        snake = []
        foodPosition = .zero
        foodColor = .red
        currentBackground = nil
    }

    func startGame() {
        state = .playing
        score = 0
        level = 1
        // Center snake of length 3
        let centerX = CGFloat(gridWidth / 2) * gridSize
        let centerY = CGFloat(gridHeight / 2) * gridSize
        snake = [
            Point(x: centerX, y: centerY),
            Point(x: centerX - gridSize, y: centerY),
            Point(x: centerX - 2*gridSize, y: centerY)
        ]
        snakeDirection = .right
        nextDirection = .right
        spawnFood()
        randomizeBackground()
        moveTimer = 0
    }

    func changeDirection(_ newDir: Direction) {
        // Queue direction change
        if !newDir.isOpposite(to: snakeDirection) {
            nextDirection = newDir
        }
    }

    func spawnFood() {
        var pos: Point
        repeat {
            let x = CGFloat(Int.random(in: 1..<(gridWidth-1))) * gridSize
            let y = CGFloat(Int.random(in: 1..<(gridHeight-1))) * gridSize
            pos = Point(x: x, y: y)
        } while snake.contains(where: { $0.x == pos.x && $0.y == pos.y })

        foodPosition = pos
        // Random color with special chance
        let colors: [UIColor] = [.red, .green, .blue, .cyan, .magenta, .yellow, .white, .gray]
        if Int.random(in: 0...10) < 2 {
            foodColor = Bool.random() ? .gold : .silver
        } else {
            foodColor = colors.randomElement() ?? .red
        }
    }

    func randomizeBackground() {
        currentBackground = backgroundImages.randomElement()
    }

    func update() {
        guard state == .playing else { return }

        moveTimer += 1/60 // assuming 60 FPS display link
        if moveTimer < moveInterval { return }
        moveTimer = 0

        // Apply queued direction
        snakeDirection = nextDirection

        // Compute new head
        guard let head = snake.first else { return }
        var newHead = head
        switch snakeDirection {
        case .up:    newHead.y -= gridSize
        case .down:  newHead.y += gridSize
        case .left:  newHead.x -= gridSize
        case .right: newHead.x += gridSize
        }

        // Check collision with walls
        let maxX = CGFloat(gridWidth) * gridSize
        let maxY = CGFloat(gridHeight) * gridSize
        if newHead.x < 0 || newHead.x >= maxX || newHead.y < 0 || newHead.y >= maxY {
            gameOver()
            return
        }

        // Check collision with self
        if snake.contains(where: { $0.x == newHead.x && $0.y == newHead.y }) {
            gameOver()
            return
        }

        // Move snake
        snake.insert(newHead, at: 0)

        // Check food
        if abs(newHead.x - foodPosition.x) < gridSize/2 && abs(newHead.y - foodPosition.y) < gridSize/2 {
            // Eat
            let points = foodColor == .gold ? 10 : foodColor == .silver ? 5 : 1
            score += points
            AudioManager.shared.playSound("food_blip")
            spawnFood()
            // Level up logic
            if score >= level * 10 {
                level += 1
                randomizeBackground()
                // Increase speed slightly? Not necessary.
            }
        } else {
            snake.removeLast()
        }
    }

    private func gameOver() {
        state = .gameOver
        AudioManager.shared.playSound("game_over")
        AudioManager.shared.stopBackgroundMusic()
    }
}
