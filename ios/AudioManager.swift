import AVFoundation

class AudioManager {
    static let shared = AudioManager()
    private var bgPlayer: AVAudioPlayer?
    private var soundPlayers: [String: AVAudioPlayer] = [:]

    private init() {
        setupAudio()
    }

    private func setupAudio() {
        // Background music
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

        // Sound effects
        let soundFiles = [
            "food_blip", "game_over", "player1_begin", "player1_wins",
            "player2_begin", "player2_wins", "its_a_draw"
        ]
        for name in soundFiles {
            // try .wav first, then .mp3 if needed
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
        soundPlayers[name]?.currentTime = 0
        soundPlayers[name]?.play()
    }
}
