import AVFoundation

class AudioManager {
    static let shared = AudioManager()
    private var bgPlayer: AVAudioPlayer?
    private var soundPlayers: [String: AVAudioPlayer] = [:]
    private var soundQueue: [String] = []

    private init() {
        setupAudio()
    }

    private func setupAudio() {
        if let url = Bundle.main.url(forResource: "background_score", withExtension: "mp3") {
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
            var ext = "wav"
            var url = Bundle.main.url(forResource: name, withExtension: ext)
            if url == nil {
                ext = "mp3"
                url = Bundle.main.url(forResource: name, withExtension: ext)
            }
            if let url = url {
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
        // If there is already a sound playing, we might want to queue it
        // For simplicity, we'll just play it immediately, but stop previous if needed
        // For game_over after wins, we'll handle in GameView
        if let player = soundPlayers[name] {
            player.currentTime = 0
            player.play()
        }
    }

    func stopAllSounds() {
        for player in soundPlayers.values {
            player.stop()
        }
    }
}