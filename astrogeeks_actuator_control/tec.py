import pigpio
import struct
import threading

from .actuator import Actuator
from .dht22 import Dht22
from .util import *

# I2C addresses
LTC2631_I2C_ADDRESS = 0x22
PCF8591_I2C_ADDRESS = 0x48

# Measured voltages for accurate temp readings
PCF8591_AGND = 0.52
PCF8591_VREF = 1.72

TEC_MAX_CURRENT = 3 # Max current that the tec module can handle (tec1-12706)
TEC_RATED_CURRENT = 5 # Max current the board can provide (100%)
TEC_DELTA_CURRENT = 0.1 # Max current step in a cycle

TEC_DELTA_TEMP_THRESHOLD = 0.5 

TEC_TEMP_LIMIT = 50.0 # Shutdown when this temp is reached on one of the tec sides

class TemperatureError(Exception):
    pass

class Tec(Actuator):
    """
    Tec class.
    You can set the case temperature, controlled by a tec.
    """
    def __init__(self, pi, name, pin):
        super().__init__(pi, name, pin)

        # Open handles for both the Adc and the Dac
        self.pcf8591Handle = pi.i2c_open(1, PCF8591_I2C_ADDRESS)
        self.ltc2631Handle = pi.i2c_open(1, LTC2631_I2C_ADDRESS)

        # Initialize the sensor to measure the case temperature
        self.dht22 = Dht22(pigpio.pi(), self.pin)
        
    def __del__(self):
        """
        Reset the tec.
        """
        self.__updateLtc2631(0)
        self.__updatePcf8591(0)

        self.pi.i2c_close(self.ltc2631Handle)
        self.pi.i2c_close(self.pcf8591Handle)

    def set(self, var):
        """
        Set a target for the tec (10.0-30.0).
        """
        self.targetTemp = clamp(var, 10.0, 30.0)
    
    async def run(self):
        """
        Update the tec by comparing the target against the case temperature.
        Warning: This function will throw an exception when temperatures higher than TEC_TEMP_LIMIT are reached.
        """
        caseTemp =  await __readDht22()
        topTemp =  __getTempTopSide()
        bottomTemp =  __getTempBottomSide()

        if (topTemp >= TEC_TEMP_LIMIT or bottomTemp >= TEC_TEMP_LIMIT):
            raise TemperatureError()

        if (abs(caseTemp - self.targetTemp) >= TEC_DELTA_TEMP_THRESHOLD):
            if (caseTemp < self.targetTemp):
                current = clamp(current + TEC_DELTA_CURRENT, 0, TEC_RATED_CURRENT)
            elif (caseTemp > self.targetTemp):
                current = clamp(current - TEC_DELTA_CURRENT, 0, TEC_RATED_CURRENT)

        self.__updateLtc2631(current)

    def __getTempTopSide():
        return  __readPcf8591(2)

    def __getTempBottomSide():
        return  __readPcf8591(3)

    def __updateLtc2631(self, current):
        value = clamp(abs(current), 0, TEC_MAX_CURRENT)
        # Calculate the word to send to LTC2631
        wordBigEndian = int(abs(current) / TEC_RATED_CURRENT * 0xFFFF)
        # Format the word in low-endian
        wordLowEndian = struct.unpack("<H", struct.pack(">H", wordBigEndian))[0]
        # Write the word to the chip
        self.pi.i2c_write_word_data(self.ltc2631Handle, 0x30, int(wordLowEndian))

    def __updatePcf8591(self, negate):
        self.pi.i2c_write_byte_data(self.pcf8591Handle, 0x40, clamp(negate, 0, 1) * 0xFF)

    def __readPcf8591(self, index):
        # refresh temperature register 3 times to be sure that we get the current temperature
        for i in range(0, 2):
            self.pi.i2c_read_byte_data(self.pcf8591Handle, 0x40 + clamp(index, 0, 3))

        # Reading to temp
        reading = self.pi.i2c_read_byte_data(self.pcf8591Handle, 0x40 + clamp(index, 0, 3))
        voltage = reading * (PCF8591_VREF - PCF8591_AGND) / 256
        temp = round((voltage + CF8591_AGND - 0.5) * 100, 1)
        return temp

    async def __readDht22(self):
        await self.dht22.read()
        return self.dht22.temperature()

    
        
    
        
        