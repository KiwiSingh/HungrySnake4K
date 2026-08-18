import AVFoundation
class AudioManager {
    static let shared = AudioManager()
    private var bgPlayer: AVAudioPlayer?
    private var soundPlayers: [String: AVAudioPlayer] = [:]
    private init() {
        setupAudio()
    }
    private func setupAudio() {
        let bgURL = Bundle.main.url(forResource: "background_score", withExtension: "mp3")
        if let url = bgURL {
            do {
                bgPlayer = try AVAudioPlayer(contentsOf: url)
                bgPlayer?.numberOfLoops = -1
                bgPlayer?.volume = 0.4
                bgPlayer?.prepareToPlay()
            } catch {
                print("BG error: \(error)")
            }
        }
        let soundFiles = [
            "food_blip", "game_over", "player1_begin", "player1_wins",
            "player2_begin", "player2_wins", "its_a_draw"
        ]
        for name in soundFiles {
            if let url = Bundle.main.url(forResource: name, withExtension: "wav") {
                do {
                    let player = try AVAudioPlayer(contentsOf: url)
                    player.volume = 0.8
                    player.prepareToPlay()
                    soundPlayers[name] = player
                } catch {
                    print("Sound \(name) error: \(error)")
                }
            }
        }
    }
    func playBackgroundMusic() {
        bgPlayer?.play()
    }
    func stopBackgroundMusic() {
        bgPlayer?.stop()
    }
    func playSound(_ name: String) {
        soundPlayers[name]?.currentTime = 0
        soundPlayers[name]?.play()
    }
}
