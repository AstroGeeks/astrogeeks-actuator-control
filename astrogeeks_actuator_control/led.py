from .actuator import Actuator
from .util import *

class Led(Actuator):
    """
    Led class.
    You set the PWM percentage of a led.
    """
    def __init__(self, pi, name, pin):
        super().__init__(pi, name, pin)

    def set(self, var):
        """
        Set a target for the led (0.0-100.0).
        """
        print("Setting Led(Pin {}) to {}".format(self.pin, var))
        self.pi.set_PWM_dutycycle(self.pin, int(clamp(var, 0.0, 100.0) * 2.55))

    def reset(self):
        """
        Turn led off.
        """
        self.pi.set_PWM_dutycycle(self.pin, 0)

    async def update(self):
        """
        Update the led.
        This does nothing.
        """
        pass


