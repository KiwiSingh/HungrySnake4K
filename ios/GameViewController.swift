import UIKit

class GameViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        let gameView = GameView(frame: view.bounds)
        view.addSubview(gameView)
        gameView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
    }
}
