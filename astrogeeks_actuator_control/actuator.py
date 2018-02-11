import abc

class Actuator(object):
    """
    Abstract actuator base class.
    You can set targets for an actuator and it will update itself when update() is called.
    """
    def __init__(self, pi, name, pin):
        self.pi = pi
        self.name = name
        self.pin = pin

    @abc.abstractmethod
    def set(self, var):
        """
        Set a target for the actuator.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def reset(self):
        """
        Reset the target for the actuator.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def update(self):
        """
        Update the actuator.
        Should be called frequently if the actuator depends on updates.
        """
        raise NotImplementedError()

    def __str__(self):
        return self.name




        