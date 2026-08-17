import pygame # type: ignore


class Controller:
    DEADZONE = 0.5

    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.controller = None
        self.stick_active = False
        self.connect_controller()

    def connect_controller(self):
        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            print(f"Controller connected: {self.controller.get_name()}")
        else:
            self.controller = None
            print("No controller detected. Keyboard controls enabled.")

    def update(self, snake):
        button_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                if self.controller is None:
                    self.connect_controller()

            elif event.type == pygame.JOYDEVICEREMOVED:
                self.controller = None
                print("Controller disconnected. Keyboard controls enabled.")

            elif event.type == pygame.JOYBUTTONDOWN:
                button_pressed = True

        if self.controller is None:
            return button_pressed

        x = self.controller.get_axis(0)
        y = self.controller.get_axis(1)

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