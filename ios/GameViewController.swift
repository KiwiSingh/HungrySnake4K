import UIKit

class GameViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()

        // Fullscreen – hide status bar and home indicator
        self.setNeedsStatusBarAppearanceUpdate()
        self.prefersHomeIndicatorAutoHidden = true

        // Prevent screen from dimming (Game Mode)
        UIApplication.shared.isIdleTimerDisabled = true

        // Create and add the game view
        let gameView = GameView(frame: view.bounds)
        view.addSubview(gameView)
        gameView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
    }

    // Hide status bar
    override var prefersStatusBarHidden: Bool {
        return true
    }

    // Prefer home indicator auto‑hidden (fullscreen)
    override var prefersHomeIndicatorAutoHidden: Bool {
        return true
    }
}