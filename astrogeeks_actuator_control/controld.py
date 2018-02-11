import atexit
import asyncio
import json
import os
import pigpio
import struct
import sys
import time
import zmq

from .config import Config

if (len(sys.argv) >= 2):
    SERVER_PORT = int(sys.argv[1])
else:
    SERVER_PORT = 4130

CONFIG_PATH = os.path.abspath("config.json")

pi = pigpio.pi()
context = zmq.Context()

config = Config(pi, CONFIG_PATH)
actuators = config.getActuators()

def main():
    """
    Receive names and targets from the clients and update the actuators accordingly.
    """
    # Create socket on *:SERVER_PORT
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:{}".format(SERVER_PORT))

    print("Starting server on port {}".format(SERVER_PORT))

    while True:
        # Check for incoming target for an actuator
        try:
            # Receive target
            message = socket.recv_string(flags = zmq.NOBLOCK)
            # Let the client know that we received the target
            socket.send_string("Target received")

            # ALT196 between strings to make sure that the separator is unique
            name = message.split("─")[0]
            target = float(message.split("─")[1])

            # Set new target
            for actuator in actuators:
                if actuator.name == name:
                    actuator.set(target)
        except zmq.Again:
            pass

        # Update all actuators
        for actuator in actuators:
            asyncio.ensure_future(actuator.update())
            
        # Wait for tasks to complete
        time.sleep(0.5)
        
@atexit.register
def exit_handler():
    """
    Finish tasks, reset actuators and close connections.
    """
    # Wait until everything has finished processing
    loop = asyncio.get_event_loop()
    for task in asyncio.Task.all_tasks():
        task.cancel()
        loop.run_until_complete(asyncio.gather(task, return_exceptions = True))

    for actuator in actuators:
        actuator.reset()

    # Clean up sockets
    context.destroy()

    # Close pigpio connection
    pi.stop()
    
if __name__ == "__main__":
    main()



