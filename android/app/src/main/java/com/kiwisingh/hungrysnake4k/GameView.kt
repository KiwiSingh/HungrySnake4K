package com.kiwisingh.hungrysnake4k

import android.content.Context
import android.graphics.Color
import android.os.Handler
import android.os.Looper
import android.view.MotionEvent
import android.view.SurfaceHolder
import android.view.SurfaceView
import kotlin.concurrent.thread
import kotlin.math.abs

class GameView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {

    private val game = SnakeGame()
    private var loopThread: Thread? = null
    private var running = true
    private var started = false
    private val handler = Handler(Looper.getMainLooper())
    private val touchStart = floatArrayOf(0f, 0f)
    private var lastTouchX = 0f
    private var lastTouchY = 0f

    init {
        holder.addCallback(this)
        isFocusable = true
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        running = true
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        running = false
        loopThread?.interrupt()
        loopThread = null
        started = false
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        if (!started) {
            started = true
            // Claude's fix: set grid dimensions and load backgrounds here
            game.setGridSize(width / 30, height / 30)
            game.loadBackgrounds(context)

            loopThread = thread {
                while (running) {
                    val startTime = System.currentTimeMillis()
                    game.update()
                    draw()
                    val elapsed = System.currentTimeMillis() - startTime
                    val sleep = maxOf(1, (1000 / 60 - elapsed).toInt())
                    Thread.sleep(sleep.toLong())
                }
            }
        }
    }

    private fun draw() {
        val canvas = holder.lockCanvas() ?: return
        try {
            canvas.drawColor(Color.BLACK)
            // gridSize is fixed at 30f (matches setGridSize calculation)
            game.draw(canvas, canvas.width, canvas.height, 30f)
        } finally {
            holder.unlockCanvasAndPost(canvas)
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        val x = event.x
        val y = event.y
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                touchStart[0] = x
                touchStart[1] = y
                lastTouchX = x
                lastTouchY = y
                if (game.state == GameState.MENU) {
                    // Single/double tap detection
                    handler.postDelayed({
                        if (game.pendingTapCount == 1) {
                            game.startGame(1)
                        }
                    }, 300)
                    game.pendingTapCount = if (game.pendingTapCount == 0) 1 else 2
                    if (game.pendingTapCount == 2) {
                        handler.removeCallbacksAndMessages(null)
                        game.startGame(2)
                        game.pendingTapCount = 0
                    }
                    return true
                } else if (game.state == GameState.DRAW_PROMPT) {
                    if (y < height / 2) {
                        game.startGame(2) // rematch
                    } else {
                        game.resetToMenu()
                    }
                    return true
                } else if (game.state == GameState.GAME_OVER) {
                    game.resetToMenu()
                    return true
                }
            }
            MotionEvent.ACTION_MOVE -> {
                if (game.state == GameState.PLAYER1_TURN || game.state == GameState.PLAYER2_TURN) {
                    val dx = x - lastTouchX
                    val dy = y - lastTouchY
                    lastTouchX = x
                    lastTouchY = y
                    if (abs(dx) < 5 && abs(dy) < 5) return true
                    val newDir = if (abs(dx) > abs(dy)) {
                        if (dx > 0) Direction.RIGHT else Direction.LEFT
                    } else {
                        if (dy > 0) Direction.DOWN else Direction.UP
                    }
                    if (!newDir.isOpposite(game.snakeDirection)) {
                        game.changeDirection(newDir)
                    }
                }
            }
        }
        return true
    }
}