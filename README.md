# Hungry Snake 4K - Cross-platform, controller-compatible Snake Game implementation

<p align="center">
  <img src="HungrySnakeIcon.png" alt="Snake Game icon" width="400">
</p>

*Hungry Snake 4K* is based heavily on Dr. Angela Yu's implementation of the classic Snake Game using the `turtle` Python library, with some key changes and additions:

- The food the snake eats is all shaped like turtles now
- The color of the food is randomized, based on a list of colors
- If the snake eats a piece of food that is golden, the user gains 10 points. If it eats a piece of food that is silver, the user gains 5 points. For all other kinds of food, the user gains 1 point.
- Controller support is provided via `pygame`. Kindly note that only the left control stick on the Sony DualSense Controller has been tested at this time.
- Cross-platform build support is provided via GitHub Actions. Kindly note that as of the time of writing, only macOS and Windows builds are provided, with a Linux build boilerplate planned for sometime in the future.

## Screenshots
![Screenshot](HungrySnakeScreenshot.png)

## AI Disclosure
The app icon for *Hungry Snake 4K* is partially AI-generated, with manually added elements via Canva.

## Contact
In case of any issues with the game or the code, open a GitHub Issue, or contact me at [kiwisingh@proton.me](mailto:kiwisingh@proton.me)
