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
    case menu, player1Turn, player2Turn, gameOver
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

    // Multiplayer
    private(set) var player1Score: Int = 0
    private(set) var player2Score: Int = 0
    private var currentPlayer: Int = 1   // 1 or 2
    private var isMultiplayer: Bool = false

    private var backgroundImages: [UIImage] = []
    private var moveTimer: TimeInterval = 0
    private let moveInterval: TimeInterval = 0.12   // ~8 moves per second

    init(gridWidth: Int, gridHeight: Int, gridSize: CGFloat) {
        self.gridWidth = gridWidth
        self.gridHeight = gridHeight
        self.gridSize = gridSize
        loadBackgrounds()
        resetToMenu()
    }

    private func loadBackgrounds() {
        // Try to load from asset catalog or bundle
        for i in 1...10 {
            let name = "background_\(String(format: "%02d", i))"
            if let img = UIImage(named: name) {
                backgroundImages.append(img)
            }
        }
        // If none found, we'll use a solid color
    }

    // MARK: - Public methods

    func setMultiplayer(_ enabled: Bool) {
        isMultiplayer = enabled
    }

    func resetToMenu() {
        state = .menu
        player1Score = 0
        player2Score = 0
        score = 0
        level = 1
        snake = []
        foodPosition = .zero
        foodColor = .red
        currentBackground = nil
        currentPlayer = 1
        AudioManager.shared.stopBackgroundMusic()
    }

    func startGame(players: Int) {
        isMultiplayer = (players == 2)
        player1Score = 0
        player2Score = 0
        currentPlayer = 1
        state = .player1Turn
        resetPlayerState()
        AudioManager.shared.playBackgroundMusic()
    }

    private func resetPlayerState() {
        score = 0
        level = 1
        // Center snake
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
        guard state == .player1Turn || state == .player2Turn else { return }

        moveTimer += 1/60
        if moveTimer < moveInterval { return }
        moveTimer = 0

        // Apply queued direction
        snakeDirection = nextDirection

        guard let head = snake.first else { return }
        var newHead = head
        switch snakeDirection {
        case .up:    newHead.y -= gridSize
        case .down:  newHead.y += gridSize
        case .left:  newHead.x -= gridSize
        case .right: newHead.x += gridSize
        }

        let maxX = CGFloat(gridWidth) * gridSize
        let maxY = CGFloat(gridHeight) * gridSize
        if newHead.x < 0 || newHead.x >= maxX || newHead.y < 0 || newHead.y >= maxY {
            playerCrashed()
            return
        }

        if snake.contains(where: { $0.x == newHead.x && $0.y == newHead.y }) {
            playerCrashed()
            return
        }

        snake.insert(newHead, at: 0)

        if abs(newHead.x - foodPosition.x) < gridSize/2 && abs(newHead.y - foodPosition.y) < gridSize/2 {
            // Eat
            let points = foodColor == .gold ? 10 : foodColor == .silver ? 5 : 1
            score += points
            AudioManager.shared.playSound("food_blip")
            spawnFood()
            if score >= level * 10 {
                level += 1
                randomizeBackground()
            }
        } else {
            snake.removeLast()
        }
    }

    private func playerCrashed() {
        AudioManager.shared.playSound("game_over")
        // Save current player's score
        if state == .player1Turn {
            player1Score = score
            if isMultiplayer {
                state = .player2Turn
                currentPlayer = 2
                // Reset snake for player 2
                resetPlayerState()
                AudioManager.shared.playSound("player2_begin")  // optional
                return
            } else {
                state = .gameOver
                AudioManager.shared.stopBackgroundMusic()
            }
        } else if state == .player2Turn {
            player2Score = score
            state = .gameOver
            AudioManager.shared.stopBackgroundMusic()
        }
    }

    func getWinner() -> String? {
        guard state == .gameOver else { return nil }
        if isMultiplayer {
            if player1Score > player2Score { return "Player 1" }
            else if player2Score > player1Score { return "Player 2" }
            else { return "Draw" }
        } else {
            return nil
        }
    }

    func getScores() -> (p1: Int, p2: Int) {
        return (player1Score, player2Score)
    }
}
