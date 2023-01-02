from signal import pause

from gpiozero import LED, Button

from common import pi_func

red = LED(17)
button = Button(2)
switch = Button(3)


class LEDController:
    """Class to track switch state and control LED behavior accordingly."""

    toggle_mode = False

    def toggle_switch_state(self) -> None:
        """Toggle led control mode.
        when:
         toggle_mode = True: toggle mode
         toggle_mode = False: momentary mode
        """
        self.toggle_mode = not self.toggle_mode
        print("Toggle Mode" if self.toggle_mode else "Momentary Mode")

    def when_pressed(self) -> None:
        """Function to control LED behavior, dependent on value of 'self.toggle_mode'."""
        if self.toggle_mode:
            return red.toggle()
        return red.on()

    def when_released(self) -> None:
        """Function to control LED behavior, dependent on value of 'self.toggle_mode'."""
        if self.toggle_mode:
            return None
        return red.off()


@pi_func
def main():
    """Control LED with button and switch to change from 'toggle' to 'momentary' mode."""
    led_controller = LEDController()
    switch.when_pressed = led_controller.toggle_switch_state
    button.when_pressed = led_controller.when_pressed
    button.when_released = led_controller.when_released
    pause()


if __name__ == "__main__":
    main()
