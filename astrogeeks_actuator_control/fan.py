from .actuator import Actuator
from .util import *

class Fan(Actuator):
    """
    Fan class.
    You enable or disable a fan.
    """
    def __init__(self, pi, name, pin):
        super().__init__(pi, name, pin)
        
    def set(self, var):
        """
        Set a target for the fan (0-1).
        """
        print("Setting Fan(Pin {}) to {}".format(self.pin, var > 0))
        self.pi.write(self.pin, int(clamp(var, 0, 1)))

    def reset(self):
        """
        Turn fan off.
        """
        self.pi.write(self.pin, 0)
        
    async def update(self):
        """
        Update the fan.
        This does nothing.
        """
        pass