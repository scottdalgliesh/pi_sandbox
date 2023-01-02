from signal import pause
from time import sleep

from gpiozero import LED, Button

from common import pi_func

red = LED(17)
button = Button(2, hold_time=3)


@pi_func
def momentary() -> None:
    """Control LED using momentary push-button."""
    button.when_pressed = red.on
    button.when_released = red.off
    pause()


@pi_func
def toggle() -> None:
    """Control LED using toggle push-button."""
    while True:
        button.wait_for_active()
        red.toggle()
        sleep(0.5)


if __name__ == "__main__":
    # momentary()
    toggle()
