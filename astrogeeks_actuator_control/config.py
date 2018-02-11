import json

from .led import Led
from .fan import Fan
from .tec import Tec

class Config(object):
    """
    Class to read the config file.
    """
    def __init__(self, pi, file):
        self.pi = pi
        self.file = file

    def getActuators(self):
        """
        Reads the config file and returns the configured actuators.
        """
        actuators = [] 
        
        with open(self.file, 'r') as f:
            config = json.load(f)
            for actuator in config['actuators']:
                actuatorClass = globals()[actuator['className']]
                actuators.append(actuatorClass(self.pi, actuator['name'], int(actuator['pin'])))

        return actuators




