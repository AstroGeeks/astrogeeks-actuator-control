"""
"""

import atexit
import pigpio
import threading
import time

DHT22_TIMEOUT = 10.0 # in seconds

class Dht22:
      """
      Based on: 
      https://github.com/joan2937/pigpio/blob/master/EXAMPLES/Python/DHT22_AM2302_SENSOR/DHT22.py
     
      A class to read relative humidity and temperature from the
      DHT22 sensor.  The sensor is also known as the AM2302.
      The sensor can be powered from the Pi 3V3 or the Pi 5V rail.
      Powering from the 3V3 rail is simpler and safer.  You may need
      to power from 5V if the sensor is connected via a long cable.
      For 3V3 operation connect pin 1 to 3V3 and pin 4 to ground.
      Connect pin 2 to a gpio.
      For 5V operation connect pin 1 to 5V and pin 4 to ground.
      The following pin 2 connection works for me.  Use at YOUR OWN RISK.
      5V--5K_resistor--+--10K_resistor--Ground
                        |
      DHT22 pin 2 -----+
                        |
      gpio ------------+
      """

      def __init__(self, pi, gpio, LED=None, power=None):
            """
            Instantiate with the Pi and gpio to which the DHT22 output
            pin is connected.
            Optionally a LED may be specified.  This will be blinked for
            each successful reading.
            Optionally a gpio used to power the sensor may be specified.
            This gpio will be set high to power the sensor.  If the sensor
            locks it will be power cycled to restart the readings.
            Taking readings more often than about once every two seconds will
            eventually cause the DHT22 to hang.  A 3 second interval seems OK.
            """

            self.pi = pi
            self.gpio = gpio
            self.LED = LED
            self.power = power

            if power is not None:
                  pi.write(power, 1)  # Switch sensor on.
                  time.sleep(2)

            self.powered = True

            self.cb = None

            self.suc_M = 0   # Successful message count.
            self.bad_CS = 0  # Bad checksum count.
            self.bad_SM = 0  # Short message count.
            self.bad_MM = 0  # Missing message count.
            self.bad_SR = 0  # Sensor reset count.

            # Power cycle if timeout > MAX_TIMEOUTS.
            self.no_response = 0
            self.MAX_NO_RESPONSE = 2

            self.rhum = -999
            self.temp = -999

            self.tov = None

            self.high_tick = 0
            self.bit = 40

            pi.set_pull_up_down(gpio, pigpio.PUD_OFF)

            pi.set_watchdog(gpio, 0)  # Kill any watchdogs.

            self.cb = pi.callback(gpio, pigpio.EITHER_EDGE, self.__cb)

      def cancel(self):
            """
            Cancel the sensor.
            """
            self.pi.set_watchdog(self.gpio, 0)

            if self.cb is not None:
                  self.cb.cancel()
                  self.cb = None

      async def read(self):
            """
            Read from the sensor.
            Warning: This function is blocking, make sure to call it from another thread
            """
            last_successful_message_count = self.__successful_message_count()

            self.__trigger()
                  
            # Wait untill we have a valid reading
            start = time.time()
            while (self.__successful_message_count() != last_successful_message_count and self.cb is not None):
                  if (time.time() - start >= DHT22_TIMEOUT):
                        print("[ERROR]: DHT22 Timed Out")
                        break
                  time.sleep(0.1)

      def temperature(self):
            """
            Return temperature.
            Call read() to renew this value.
            """
            return self.temp

      def humidity(self):
            """
            Return relative humidity.
            Call read() to renew this value.
            """
            return self.rhum

      def __cb(self, gpio, level, tick):
            """
            Accumulate the 40 data bits.  Format into 5 bytes, humidity high,
            humidity low, temperature high, temperature low, checksum.
            """
            diff = pigpio.tickDiff(self.high_tick, tick)

            if level == 0:
                  # Edge length determines if bit is 1 or 0.
                  if diff >= 50:
                        val = 1
                        if diff >= 200:   # Bad bit?
                              self.CS = 256  # Force bad checksum.
                  else:
                        val = 0

                  if self.bit >= 40:  # Message complete.
                        self.bit = 40

                  elif self.bit >= 32:  # In checksum byte.
                        self.CS  = (self.CS << 1)  + val

                        if self.bit == 39:
                              # 40th bit received.

                              self.pi.set_watchdog(self.gpio, 0)

                              self.no_response = 0

                              total = self.hH + self.hL + self.tH + self.tL

                              if (total & 255) == self.CS:  # Is checksum ok?
                                    self.rhum = ((self.hH << 8) + self.hL) * 0.1

                                    if self.tH & 128:  # Negative temperature.
                                          mult = -0.1
                                          self.tH = self.tH & 127
                                    else:
                                          mult = 0.1

                                    self.temp = ((self.tH << 8) + self.tL) * mult

                                    self.tov = time.time()

                                    self.suc_M += 1
                                    
                                    if self.LED is not None:
                                          self.pi.write(self.LED, 0)
                              else:
                                    self.bad_CS += 1

                  elif self.bit >= 24:  # in temp low byte
                        self.tL = (self.tL << 1) + val

                  elif self.bit >= 16:  # in temp high byte
                        self.tH = (self.tH << 1) + val

                  elif self.bit >= 8:  # in humidity low byte
                        self.hL = (self.hL << 1) + val

                  elif self.bit >= 0:  # in humidity high byte
                        self.hH = (self.hH << 1) + val

                  else:               # header bits
                        pass

                  self.bit += 1

            elif level == 1:
                  self.high_tick = tick
                  if diff > 250000:
                        self.bit = -2
                        self.hH = 0
                        self.hL = 0
                        self.tH = 0
                        self.tL = 0
                        self.CS = 0

            else:  # level == pigpio.TIMEOUT:
                  self.pi.set_watchdog(self.gpio, 0)
                  if self.bit < 8:       # Too few data bits received.
                        self.bad_MM += 1    # Bump missing message count.
                        self.no_response += 1
                        if self.no_response > self.MAX_NO_RESPONSE:
                              self.no_response = 0
                              self.bad_SR += 1  # Bump sensor reset count.
                              if self.power is not None:
                                    self.powered = False
                                    self.pi.write(self.power, 0)
                                    time.sleep(2)
                                    self.pi.write(self.power, 1)
                                    time.sleep(2)
                                    self.powered = True
                  elif self.bit < 39:    # Short message receieved.
                        self.bad_SM += 1    # Bump short message count.
                        self.no_response = 0
                  else:                  # Full message received.
                        self.no_response = 0

      def __successful_message_count(self):
            """
            Return the count of successful messages.
            """
            return self.suc_M

      def __staleness(self):
            """Return time since measurement made."""
            if self.tov is not None:
                  return time.time() - self.tov
            else:
                  return -999

      def __bad_checksum(self):
            """Return count of messages received with bad checksums."""
            return self.bad_CS

      def __shortMessage(self):
            """
            Return count of short messages.
            """
            return self.bad_SM

      def __missing_message(self):
            """Return count of missing messages."""
            return self.bad_MM

      def __sensor_resets(self):
            """
            Return count of power cycles because of sensor hangs.
            """
            return self.bad_SR

      def __trigger(self):
            """
            Trigger a new relative humidity and temperature reading.
            """
            if self.powered:
                  if self.LED is not None:
                        self.pi.write(self.LED, 1)

                  self.pi.write(self.gpio, pigpio.LOW)
                  time.sleep(0.017)  # 17 ms
                  self.pi.set_mode(self.gpio, pigpio.INPUT)
                  self.pi.set_watchdog(self.gpio, 200)
