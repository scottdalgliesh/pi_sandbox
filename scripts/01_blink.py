from time import sleep

from gpiozero import LED

from common import pi_func

red = LED(17)


@pi_func
def main() -> None:
    """Blink led."""
    while True:
        red.on()
        print("LED is on.")
        sleep(1)
        red.off()
        sleep(1)
        print("LED is off.")


if __name__ == "__main__":
    main()
