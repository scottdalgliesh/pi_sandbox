import time
from datetime import datetime, timedelta
from signal import pause
from typing import Optional

from gpiozero import LED, Button
from RPLCD.i2c import CharLCD

from common import pi_func

red = LED(26)
yellow = LED(19)
blue = LED(13)

red_button = Button(10)
yellow_button = Button(9, hold_time=5)
blue_button = Button(11)

lcd = CharLCD("PCF8574", 0x27)


class Player:
    """Player for raspberry pi chess clock. Default player time is 10 minutes."""

    time_remaining: timedelta = timedelta(minutes=10)
    _is_active: bool = False
    time_activated: Optional[datetime] = None
    max_time = 30

    def __init__(self, led: LED):
        self.led = led

    @property
    def is_active(self) -> bool:
        """Controls player status light indicator."""
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool) -> None:
        self.led.value = int(value)
        self._is_active = value

    def adjust_time_remaining(self) -> None:
        """Allow user to adjust time_remaining prior to initiating the game.
        Each button press decrements time_remaining by 1 minute.
        """
        if self.time_remaining > timedelta(minutes=1):
            self.time_remaining -= timedelta(minutes=1)
        else:
            self.time_remaining = timedelta(minutes=self.max_time)

    def start_turn(self) -> None:
        """Initiates turn. If already initiated, does nothing."""
        if self.is_active is False:
            self.is_active = True
            self.time_activated = datetime.now()

    def get_time_remaining(self) -> str:
        """Get time remaining for player, return as string in format: "MM:SS"."""
        # get remaining time
        if self.is_active:
            time_remaining = self.time_remaining - (datetime.now() - self.time_activated)
        else:
            time_remaining = self.time_remaining

        # handle case of negative time remaining (overtime condition)
        sign = "-" if time_remaining.total_seconds() < 0 else ""
        time_remaining = abs(time_remaining)

        # format result for display
        minutes, seconds = divmod(int(time_remaining.total_seconds()), 60)
        return f"{sign}{minutes:02d}:{seconds:02d}"

    def end_turn(self) -> None:
        """Ends turn. If already ended, does nothing."""
        if self.is_active is True:
            self.time_remaining -= datetime.now() - self.time_activated
            self.is_active = False
            self.time_activated = None


class ChessClock:
    """Raspberry Pi chess clock."""

    default_minutes = 10

    def __init__(self) -> None:
        self.initiate_game()

    @property
    def is_paused(self) -> bool:
        """Controls game (pause) status light indicator."""
        return self._is_paused

    @is_paused.setter
    def is_paused(self, value: bool) -> None:
        yellow.value = int(value)
        self._is_paused = value

    def initiate_game(self) -> None:
        """Initiate a new game."""
        # reset lcd in case of improper shutdown
        lcd.clear()
        lcd.cursor_pos = (0, 0)

        # pre-game phase
        self.is_started = False
        self.is_paused = True
        self.player1 = Player(led=red)
        self.player2 = Player(led=blue)
        red_button.when_pressed = self.player1.adjust_time_remaining
        blue_button.when_pressed = self.player2.adjust_time_remaining
        yellow_button.when_pressed = lambda: setattr(self, "is_started", True)
        while self.is_started is False:
            self.print_time_remaining()
            time.sleep(0.1)

        # game phase
        red_button.when_pressed = self.red_button
        blue_button.when_pressed = self.blue_button
        yellow_button.when_pressed = self.yellow_button
        while True:
            if yellow_button.is_held:
                return self.initiate_game()
            self.print_time_remaining()
            time.sleep(0.1)

    def blue_button(self):
        """Initiate player1's turn."""
        self.is_paused = False
        self.player2.end_turn()
        self.player1.start_turn()

    def red_button(self):
        """Initiate player2's turn."""
        self.is_paused = False
        self.player1.end_turn()
        self.player2.start_turn()

    def yellow_button(self):
        """Pause game."""
        self.is_paused = True
        self.player1.end_turn()
        self.player2.end_turn()

    def print_time_remaining(self) -> None:
        """Print out time remaining"""
        player1_time = self.player1.get_time_remaining()
        player2_time = self.player2.get_time_remaining()
        lcd.cursor_pos = (0, 0)
        lcd.write_string(f"{'Player1':<8}{'Player2':>8}\n\r{player1_time:<8}{player2_time:>8}")


@pi_func
def main():
    """Control LED with button and switch to change from 'toggle' to 'momentary' mode."""
    ChessClock()
    pause()


if __name__ == "__main__":
    try:
        main()
    finally:
        lcd.clear()
