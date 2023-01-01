import functools
import os
from typing import Callable


def pi_func(func: Callable):
    """Decorator for use on main function controlling raspberry pi.

    This decorator performs the following:
        - Set environment variable to select native pin factory
        - Wrap function in a try/except block to ensure that all raspberry pi pins
          are safely shut down in the event of an exception.
    """

    @functools.wraps(func)
    def wrapper_pi_func(*args, **kwargs):
        try:
            os.environ["GPIOZERO_PIN_FACTORY"] = "rpigpio"
            result = func(*args, **kwargs)
        except KeyboardInterrupt:
            result = None
            print("Program halted by user")
        except Exception as exc:  # pylint: disable=broad-except
            result = None
            print(f"Exception encountered while executing function: {func.__name__}")
            print(exc)
        return result

    return wrapper_pi_func
