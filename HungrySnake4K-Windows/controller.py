import pygame  # type: ignore

class Controller:
    DEADZONE = 0.5

    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.controller = None
        self.stick_active = False
        self.button_states = {}

        if self.connect_controller():
            print(f"Controller connected: {self.controller.get_name()}")
        else:
            print("No controller detected. Keyboard controls enabled.")

    def connect_controller(self):
        if pygame.joystick.get_count() == 0:
            return False

        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
        return True

    def update(self, snake):
        pygame.event.pump()

        if self.controller is None:
            self.connect_controller()
            return []

        new_presses = []

        try:
            # Track state for all buttons to emit single "press down" events
            for button in range(self.controller.get_numbuttons()):
                is_pressed = self.controller.get_button(button)
                if is_pressed and not self.button_states.get(button, False):
                    new_presses.append(button)
                self.button_states[button] = is_pressed

            x = self.controller.get_axis(0)
            y = self.controller.get_axis(1)

        except pygame.error:
            self.controller = None
            self.stick_active = False
            self.button_states.clear()
            print("Controller disconnected. Keyboard controls enabled.")
            return []

        # Joystick Deadzone and Movement Logic
        if abs(x) < self.DEADZONE and abs(y) < self.DEADZONE:
            self.stick_active = False
            return new_presses

        if self.stick_active:
            return new_presses

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
        return new_presses