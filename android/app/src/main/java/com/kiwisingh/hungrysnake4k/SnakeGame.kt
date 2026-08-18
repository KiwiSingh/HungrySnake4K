package com.kiwisingh.hungrysnake4k

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.RectF
import kotlin.math.abs
import kotlin.random.Random

enum class Direction {
    UP, DOWN, LEFT, RIGHT;
    fun isOpposite(other: Direction) = (this == UP && other == DOWN) ||
            (this == DOWN && other == UP) ||
            (this == LEFT && other == RIGHT) ||
            (this == RIGHT && other == LEFT)
}

enum class GameState {
    MENU, PLAYER1_TURN, PLAYER2_TURN, GAME_OVER, DRAW_PROMPT
}

data class Point(var x: Float, var y: Float)

class SnakeGame {
    var state = GameState.MENU
    private var gridWidth = 0
    private var gridHeight = 0
    private lateinit var snake: MutableList<Point>
    var snakeDirection = Direction.RIGHT
    private var nextDirection = Direction.RIGHT
    private var food = Point(0f, 0f)
    private var foodColor = Color.RED
    var score = 0
    var level = 1
    var currentBackground: Bitmap? = null
    var player1Score = 0
    var player2Score = 0
    private var isMultiplayer = false
    private var backgroundImages = mutableListOf<Bitmap>()
    private var moveTimer = 0f
    private val moveInterval = 0.12f // seconds
    var pendingTapCount = 0

    init {
        resetToMenu()
    }

    fun setGridSize(width: Int, height: Int) {
        gridWidth = width
        gridHeight = height
    }

    // Added by Claude – loads backgrounds from drawable resources
    fun loadBackgrounds(context: Context) {
        for (i in 1..10) {
            val name = "background_" + String.format("%02d", i)
            val id = context.resources.getIdentifier(name, "drawable", context.packageName)
            if (id != 0) {
                backgroundImages.add(BitmapFactory.decodeResource(context.resources, id))
            }
        }
    }

    fun resetToMenu() {
        state = GameState.MENU
        player1Score = 0
        player2Score = 0
        score = 0
        level = 1
        snake = mutableListOf()
        food = Point(0f, 0f)
        foodColor = Color.RED
        currentBackground = null
        snakeDirection = Direction.RIGHT
        nextDirection = Direction.RIGHT
        pendingTapCount = 0
        AudioManager.stopBackgroundMusic()
    }

    fun startGame(players: Int) {
        isMultiplayer = players == 2
        player1Score = 0
        player2Score = 0
        state = GameState.PLAYER1_TURN
        resetPlayerState()
        AudioManager.playBackgroundMusic()
        if (players == 2) AudioManager.playSound("player1_begin")
    }

    private fun resetPlayerState() {
        score = 0
        level = 1
        val centerX = gridWidth / 2f * 30f
        val centerY = gridHeight / 2f * 30f
        snake = mutableListOf(
            Point(centerX, centerY),
            Point(centerX - 30f, centerY),
            Point(centerX - 60f, centerY)
        )
        snakeDirection = Direction.RIGHT
        nextDirection = Direction.RIGHT
        spawnFood()
        randomizeBackground()
        moveTimer = 0f
    }

    fun changeDirection(newDir: Direction) {
        if (!newDir.isOpposite(snakeDirection)) {
            nextDirection = newDir
        }
    }

    private fun spawnFood() {
        var pos: Point
        var ok: Boolean
        do {
            val x = Random.nextInt(1, gridWidth - 1) * 30f
            val y = Random.nextInt(1, gridHeight - 1) * 30f
            pos = Point(x, y)
            ok = !snake.any { it.x == pos.x && it.y == pos.y }
        } while (!ok)
        food = pos
        foodColor = if (Random.nextDouble() < 0.2) {
            if (Random.nextBoolean()) Color.YELLOW else Color.GRAY // gold/silver
        } else {
            listOf(Color.RED, Color.GREEN, Color.BLUE, Color.CYAN, Color.MAGENTA, Color.WHITE).random()
        }
    }

    private fun randomizeBackground() {
        currentBackground = if (backgroundImages.isNotEmpty()) {
            backgroundImages.random()
        } else {
            null
        }
    }

    fun update() {
        if (state != GameState.PLAYER1_TURN && state != GameState.PLAYER2_TURN) return
        moveTimer += 1 / 60f
        if (moveTimer < moveInterval) return
        moveTimer = 0f

        snakeDirection = nextDirection

        val head = snake.first()
        val newHead = Point(head.x, head.y)
        when (snakeDirection) {
            Direction.UP -> newHead.y -= 30f
            Direction.DOWN -> newHead.y += 30f
            Direction.LEFT -> newHead.x -= 30f
            Direction.RIGHT -> newHead.x += 30f
        }

        val maxX = gridWidth * 30f
        val maxY = gridHeight * 30f
        if (newHead.x < 0 || newHead.x >= maxX || newHead.y < 0 || newHead.y >= maxY) {
            playerCrashed()
            return
        }

        if (snake.any { it.x == newHead.x && it.y == newHead.y }) {
            playerCrashed()
            return
        }

        snake.add(0, newHead)

        if (abs(newHead.x - food.x) < 15f && abs(newHead.y - food.y) < 15f) {
            val points = when (foodColor) {
                Color.YELLOW -> 10
                Color.GRAY -> 5
                else -> 1
            }
            score += points
            AudioManager.playSound("food_blip")
            spawnFood()
            if (score >= level * 10) {
                level++
                randomizeBackground()
            }
        } else {
            snake.removeAt(snake.size - 1)
        }
    }

    private fun playerCrashed() {
        if (state == GameState.PLAYER1_TURN) {
            player1Score = score
            if (isMultiplayer) {
                state = GameState.PLAYER2_TURN
                resetPlayerState()
                AudioManager.playSound("player2_begin")
                return
            } else {
                state = GameState.GAME_OVER
                AudioManager.stopBackgroundMusic()
                AudioManager.playSound("game_over")
                return
            }
        } else if (state == GameState.PLAYER2_TURN) {
            player2Score = score
            if (player1Score > player2Score) {
                AudioManager.playSound("player1_wins")
                state = GameState.GAME_OVER
                AudioManager.stopBackgroundMusic()
                handler.postDelayed({ AudioManager.playSound("game_over") }, 1500)
            } else if (player2Score > player1Score) {
                AudioManager.playSound("player2_wins")
                state = GameState.GAME_OVER
                AudioManager.stopBackgroundMusic()
                handler.postDelayed({ AudioManager.playSound("game_over") }, 1500)
            } else {
                AudioManager.playSound("its_a_draw")
                state = GameState.DRAW_PROMPT
                AudioManager.stopBackgroundMusic()
            }
        }
    }

    fun getWinner(): String? {
        if (state == GameState.GAME_OVER && isMultiplayer) {
            return if (player1Score > player2Score) "Player 1"
            else if (player2Score > player1Score) "Player 2"
            else "Draw"
        }
        return null
    }

    fun getScores() = Pair(player1Score, player2Score)

    // Claude's draw signature – includes gridSize parameter
    fun draw(canvas: Canvas, width: Int, height: Int, gridSize: Float) {
        if (currentBackground != null) {
            canvas.drawBitmap(currentBackground!!, null, RectF(0f, 0f, width.toFloat(), height.toFloat()), null)
        } else {
            canvas.drawColor(Color.DKGRAY)
        }

        val foodPaint = Paint().apply { color = foodColor }
        canvas.drawRect(food.x - 15f, food.y - 15f, food.x + 15f, food.y + 15f, foodPaint)

        val snakePaint = Paint().apply { color = Color.YELLOW }
        val strokePaint = Paint().apply { color = Color.RED; style = Paint.Style.STROKE; strokeWidth = 2f }
        for (seg in snake) {
            canvas.drawRect(seg.x - 14f, seg.y - 14f, seg.x + 14f, seg.y + 14f, snakePaint)
            canvas.drawRect(seg.x - 14f, seg.y - 14f, seg.x + 14f, seg.y + 14f, strokePaint)
        }

        val textPaint = Paint().apply { color = Color.WHITE; textSize = 40f; isFakeBoldText = true }
        canvas.drawText("Level: $level  Score: $score", 20f, 60f, textPaint)

        if (state == GameState.PLAYER1_TURN || state == GameState.PLAYER2_TURN) {
            val player = if (state == GameState.PLAYER1_TURN) "1" else "2"
            canvas.drawText("Player $player's turn", width / 2f - 150f, height - 100f, textPaint)
        }

        when (state) {
            GameState.GAME_OVER -> drawGameOver(canvas, width, height)
            GameState.DRAW_PROMPT -> drawDrawPrompt(canvas, width, height)
            GameState.MENU -> drawMenu(canvas, width, height)
            else -> {}
        }
    }

    private fun drawMenu(canvas: Canvas, w: Int, h: Int) {
        canvas.drawColor(Color.BLUE)
        val paint = Paint().apply { color = Color.WHITE; textSize = 80f; isFakeBoldText = true }
        canvas.drawText("HUNGRY SNAKE 4K", w / 2f - 300f, h / 2f - 150f, paint)
        val subPaint = Paint().apply { color = Color.WHITE; textSize = 40f }
        canvas.drawText("Tap for 1 Player  |  Double tap for 2 Players", w / 2f - 350f, h / 2f + 50f, subPaint)
    }

    private fun drawGameOver(canvas: Canvas, w: Int, h: Int) {
        val overlay = Paint().apply { color = Color.argb(150, 0, 0, 0) }
        canvas.drawRect(0f, 0f, w.toFloat(), h.toFloat(), overlay)

        val paint = Paint().apply { color = Color.RED; textSize = 100f; isFakeBoldText = true }
        val winner = getWinner()
        val text = when {
            winner == "Draw" -> "IT'S A DRAW!"
            winner != null -> "$winner WINS!"
            else -> "GAME OVER"
        }
        canvas.drawText(text, w / 2f - 300f, h / 2f - 150f, paint)

        val scores = getScores()
        val scorePaint = Paint().apply { color = Color.WHITE; textSize = 60f }
        canvas.drawText("P1: ${scores.first}  P2: ${scores.second}", w / 2f - 200f, h / 2f - 50f, scorePaint)

        val tapPaint = Paint().apply { color = Color.LTGRAY; textSize = 40f }
        canvas.drawText("Tap to return to menu", w / 2f - 250f, h / 2f + 100f, tapPaint)
    }

    private fun drawDrawPrompt(canvas: Canvas, w: Int, h: Int) {
        val overlay = Paint().apply { color = Color.argb(200, 0, 0, 0) }
        canvas.drawRect(0f, 0f, w.toFloat(), h.toFloat(), overlay)

        val paint = Paint().apply { color = Color.argb(255, 255, 165, 0); textSize = 100f; isFakeBoldText = true }
        canvas.drawText("IT'S A DRAW!", w / 2f - 300f, h / 2f - 200f, paint)

        val scores = getScores()
        val scorePaint = Paint().apply { color = Color.WHITE; textSize = 60f }
        canvas.drawText("P1: ${scores.first}  P2: ${scores.second}", w / 2f - 200f, h / 2f - 100f, scorePaint)

        val rematchPaint = Paint().apply { color = Color.GREEN; textSize = 50f }
        canvas.drawText("Tap TOP for Rematch", w / 2f - 300f, h / 2f + 50f, rematchPaint)

        val menuPaint = Paint().apply { color = Color.RED; textSize = 50f }
        canvas.drawText("Tap BOTTOM for Menu", w / 2f - 300f, h / 2f + 150f, menuPaint)
    }

    companion object {
        private val handler = android.os.Handler(android.os.Looper.getMainLooper())
    }
}