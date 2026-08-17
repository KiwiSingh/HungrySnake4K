import pygame # type: ignore


class Controller:
    DEADZONE = 0.5

    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.controller = None
        self.stick_active = False
        self.button_active = False

        if self.connect_controller():
            print(f"Controller connected: {self.controller.get_name()}")
        else:
            print("No controller detected. Keyboard controls enabled.")

    def connect_controller(self):
        if pygame.joystick.get_count() == 0:
            return False

        self.controller = pygame.joystick.Joystick(0)
        return True

    def update(self, snake):
        pygame.event.pump()

        if self.controller is None:
            self.connect_controller()
            return False

        try:
            button_is_held = any(
                self.controller.get_button(button)
                for button in range(self.controller.get_numbuttons())
            )

            button_pressed = button_is_held and not self.button_active
            self.button_active = button_is_held

            x = self.controller.get_axis(0)
            y = self.controller.get_axis(1)

        except pygame.error:
            self.controller = None
            self.stick_active = False
            self.button_active = False
            print("Controller disconnected. Keyboard controls enabled.")
            return False

        if abs(x) < self.DEADZONE and abs(y) < self.DEADZONE:
            self.stick_active = False
            return button_pressed

        if self.stick_active:
            return button_pressed

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
        return button_pressed