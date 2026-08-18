package com.kiwisingh.hungrysnake4k

import android.content.Context
import android.media.MediaPlayer

object AudioManager {
    private var bgPlayer: MediaPlayer? = null
    private val sfxPlayers = mutableMapOf<String, MediaPlayer>()

    fun init(context: Context) {
        // Background music
        try {
            val afd = context.resources.openRawResourceFd(R.raw.background_score)
            bgPlayer = MediaPlayer().apply {
                setDataSource(afd.fileDescriptor, afd.startOffset, afd.length)
                isLooping = true
                setVolume(0.4f, 0.4f)
                prepare()
            }
            afd.close()
        } catch (e: Exception) {
            e.printStackTrace()
        }

        // Sound effects
        val soundNames = listOf(
            "food_blip", "game_over", "player1_begin", "player1_wins",
            "player2_begin", "player2_wins", "its_a_draw"
        )
        for (name in soundNames) {
            try {
                val id = context.resources.getIdentifier(name, "raw", context.packageName)
                if (id != 0) {
                    val afd = context.resources.openRawResourceFd(id)
                    val mp = MediaPlayer().apply {
                        setDataSource(afd.fileDescriptor, afd.startOffset, afd.length)
                        setVolume(0.8f, 0.8f)
                        prepare()
                    }
                    afd.close()
                    sfxPlayers[name] = mp
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun playBackgroundMusic() {
        bgPlayer?.start()
    }

    fun stopBackgroundMusic() {
        bgPlayer?.pause()
        bgPlayer?.seekTo(0)
    }

    fun playSound(name: String) {
        sfxPlayers[name]?.apply {
            seekTo(0)
            start()
        }
    }

    fun release() {
        bgPlayer?.release()
        bgPlayer = null
        sfxPlayers.values.forEach { it.release() }
        sfxPlayers.clear()
    }
}