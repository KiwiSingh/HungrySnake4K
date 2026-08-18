package com.kiwisingh.hungrysnake4k

import android.os.Bundle
import android.view.WindowManager
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Fullscreen and keep screen on
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        supportActionBar?.hide()

        // Initialize audio (Claude’s fix)
        AudioManager.init(this)

        setContentView(GameView(this))
    }

    override fun onDestroy() {
        super.onDestroy()
        AudioManager.release()
    }
}