import pygame


class Controller:
    DEADZONE = 0.5

    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.controller = None
        self.stick_active = False

        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            print(f"Controller connected: {self.controller.get_name()}")
        else:
            print("No controller detected. Keyboard controls enabled.")

    def update(self, snake):
        if self.controller is None:
            return

        pygame.event.pump()

        x = self.controller.get_axis(0)
        y = self.controller.get_axis(1)

        if abs(x) < self.DEADZONE and abs(y) < self.DEADZONE:
            self.stick_active = False
            return

        if self.stick_active:
            return

        if abs(x) > abs(y):
            if x < -self.DEADZONE:
                snake.left()
            elif x > self.DEADZONE:
                snake.right()
        else:
            if y < -self.DEADZONE:
                snake.up()
            elif y > self.DEADZONE:
                snake.down()

        self.stick_active = True