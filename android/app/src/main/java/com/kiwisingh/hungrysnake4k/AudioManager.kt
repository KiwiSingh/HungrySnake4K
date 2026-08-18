package com.kiwisingh.hungrysnake4k

import android.content.Context
import android.media.MediaPlayer
import android.util.Log

object AudioManager {
    private const val TAG = "AudioManager"
    private var bgPlayer: MediaPlayer? = null
    private val sfxPlayers = mutableMapOf<String, MediaPlayer>()

    fun init(context: Context) {
        // Background music
        try {
            val afd = context.resources.openRawResourceFd(R.raw.background_score)
            if (afd != null) {
                bgPlayer = MediaPlayer().apply {
                    setDataSource(afd.fileDescriptor, afd.startOffset, afd.length)
                    isLooping = true
                    setVolume(0.4f, 0.4f)
                    prepare()
                    Log.d(TAG, "Background music loaded successfully")
                }
                afd.close()
            } else {
                Log.e(TAG, "background_score.mp3 not found in raw/")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to load background music: ${e.message}")
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
                    if (afd != null) {
                        val mp = MediaPlayer().apply {
                            setDataSource(afd.fileDescriptor, afd.startOffset, afd.length)
                            setVolume(0.8f, 0.8f)
                            prepare()
                        }
                        afd.close()
                        sfxPlayers[name] = mp
                        Log.d(TAG, "SFX loaded: $name")
                    } else {
                        Log.e(TAG, "SFX file not found: $name")
                    }
                } else {
                    Log.e(TAG, "No resource ID for: $name")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Failed to load SFX $name: ${e.message}")
            }
        }
    }

    fun playBackgroundMusic() {
        try {
            bgPlayer?.let {
                if (!it.isPlaying) {
                    it.start()
                    Log.d(TAG, "Background music started")
                }
            } ?: Log.w(TAG, "Background player is null, cannot play")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to play background music: ${e.message}")
        }
    }

    fun stopBackgroundMusic() {
        try {
            bgPlayer?.let {
                if (it.isPlaying) {
                    it.pause()
                    it.seekTo(0)
                    Log.d(TAG, "Background music stopped")
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to stop background music: ${e.message}")
        }
    }

    fun playSound(name: String) {
        try {
            sfxPlayers[name]?.let {
                it.seekTo(0)
                it.start()
                Log.d(TAG, "Playing SFX: $name")
            } ?: Log.w(TAG, "SFX not found: $name")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to play SFX $name: ${e.message}")
        }
    }

    fun release() {
        try {
            bgPlayer?.release()
            bgPlayer = null
            sfxPlayers.values.forEach { it.release() }
            sfxPlayers.clear()
            Log.d(TAG, "Audio resources released")
        } catch (e: Exception) {
            Log.e(TAG, "Error releasing audio: ${e.message}")
        }
    }
}