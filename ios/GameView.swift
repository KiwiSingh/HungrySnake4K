import UIKit

class GameView: UIView {
    private var game: SnakeGame!
    private var displayLink: CADisplayLink!
    private let gridSize: CGFloat = 30.0
    private var touchStart: CGPoint?
    private var lastDirection: Direction = .right

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupGame()
        setupGestures()
        setupDisplayLink()
        AudioManager.shared.playBackgroundMusic()
    }

    required init?(coder: NSCoder) { fatalError("init(coder:) has not been implemented") }

    private func setupGame() {
        let width = Int(frame.width / gridSize)
        let height = Int(frame.height / gridSize)
        game = SnakeGame(gridWidth: width, gridHeight: height, gridSize: gridSize)
    }

    private func setupGestures() {
        let pan = UIPanGestureRecognizer(target: self, action: #selector(handlePan(_:)))
        addGestureRecognizer(pan)
        let tap = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        addGestureRecognizer(tap)
    }

    @objc private func handleTap(_ gesture: UITapGestureRecognizer) {
        if game.state == .menu {
            game.startGame()
            AudioManager.shared.playSound("player1_begin")
        } else if game.state == .gameOver {
            game.resetToMenu()
            AudioManager.shared.stopBackgroundMusic()
        }
        setNeedsDisplay()
    }

    @objc private func handlePan(_ gesture: UIPanGestureRecognizer) {
        guard game.state == .playing else { return }
        let velocity = gesture.velocity(in: self)
        let dx = velocity.x
        let dy = velocity.y
        if abs(dx) < 20 && abs(dy) < 20 { return }
        var newDir: Direction
        if abs(dx) > abs(dy) {
            newDir = dx > 0 ? .right : .left
        } else {
            newDir = dy > 0 ? .down : .up
        }
        if !newDir.isOpposite(to: game.snakeDirection) {
            game.changeDirection(newDir)
        }
    }

    private func setupDisplayLink() {
        displayLink = CADisplayLink(target: self, selector: #selector(update))
        displayLink.add(to: .main, forMode: .common)
    }

    @objc private func update() {
        game.update()
        setNeedsDisplay()
    }

    override func draw(_ rect: CGRect) {
        guard let context = UIGraphicsGetCurrentContext() else { return }
        context.setFillColor(UIColor.black.cgColor)
        context.fill(rect)

        switch game.state {
        case .menu:
            drawMenu(context)
        case .playing:
            drawGame(context)
        case .gameOver:
            drawGame(context)
            drawGameOver(context)
        }
    }

    private func drawMenu(_ context: CGContext) {
        context.setFillColor(UIColor.blue.cgColor)
        context.fill(bounds)

        let title = "HUNGRY SNAKE 4K"
        let attrTitle = NSAttributedString(string: title, attributes: [
            .font: UIFont.boldSystemFont(ofSize: 40),
            .foregroundColor: UIColor.red
        ])
        let size = attrTitle.size()
        attrTitle.draw(at: CGPoint(x: (bounds.width - size.width)/2, y: 100))

        let instr = "Tap to start"
        let attrInstr = NSAttributedString(string: instr, attributes: [
            .font: UIFont.systemFont(ofSize: 24),
            .foregroundColor: UIColor.white
        ])
        let sizeInstr = attrInstr.size()
        attrInstr.draw(at: CGPoint(x: (bounds.width - sizeInstr.width)/2, y: 200))
    }

    private func drawGame(_ context: CGContext) {
        if let bg = game.currentBackground {
            bg.draw(in: bounds)
        } else {
            context.setFillColor(UIColor.darkGreen.cgColor)
            context.fill(bounds)
        }

        // Food
        let foodRect = CGRect(x: game.foodPosition.x - gridSize/2,
                              y: game.foodPosition.y - gridSize/2,
                              width: gridSize, height: gridSize)
        context.setFillColor(game.foodColor.cgColor)
        context.fill(foodRect)

        // Snake
        for segment in game.snake {
            let segRect = CGRect(x: segment.x - gridSize/2 + 1,
                                 y: segment.y - gridSize/2 + 1,
                                 width: gridSize - 2, height: gridSize - 2)
            context.setFillColor(UIColor.yellow.cgColor)
            context.fill(segRect)
            context.setStrokeColor(UIColor.red.cgColor)
            context.setLineWidth(2)
            context.stroke(segRect)
        }

        // Score
        let scoreText = "Level: \(game.level)  Score: \(game.score)"
        let attrScore = NSAttributedString(string: scoreText, attributes: [
            .font: UIFont.boldSystemFont(ofSize: 20),
            .foregroundColor: UIColor.white
        ])
        attrScore.draw(at: CGPoint(x: 20, y: 20))
    }

    private func drawGameOver(_ context: CGContext) {
        let overlay = UIBezierPath(rect: bounds)
        context.setFillColor(UIColor(white: 0, alpha: 0.5).cgColor)
        overlay.fill()

        let overText = "GAME OVER"
        let attr = NSAttributedString(string: overText, attributes: [
            .font: UIFont.boldSystemFont(ofSize: 48),
            .foregroundColor: UIColor.red
        ])
        let size = attr.size()
        attr.draw(at: CGPoint(x: (bounds.width - size.width)/2, y: bounds.height/2 - 60))

        let scoreText = "Score: \(game.score)"
        let attrScore = NSAttributedString(string: scoreText, attributes: [
            .font: UIFont.systemFont(ofSize: 30),
            .foregroundColor: UIColor.white
        ])
        let sizeScore = attrScore.size()
        attrScore.draw(at: CGPoint(x: (bounds.width - sizeScore.width)/2, y: bounds.height/2))

        let tapText = "Tap to return"
        let attrTap = NSAttributedString(string: tapText, attributes: [
            .font: UIFont.systemFont(ofSize: 20),
            .foregroundColor: UIColor.lightGray
        ])
        let sizeTap = attrTap.size()
        attrTap.draw(at: CGPoint(x: (bounds.width - sizeTap.width)/2, y: bounds.height/2 + 60))
    }
}
