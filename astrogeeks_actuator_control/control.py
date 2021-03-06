import atexit
import sys
import zmq

name = sys.argv[1]
target = sys.argv[2]

if (len(sys.argv) >= 4):
    SERVER_PORT = int(sys.argv[3])
else:
    SERVER_PORT = 4130

context = zmq.Context()

def main():
    """
    Send name and target to the daemon
    """
    # Create socket
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:{}".format(SERVER_PORT))

    # Send target
    # ALT196 between strings to make sure that the separator is unique
    socket.send_string(name + "─" + target)
    socket.recv_string()

@atexit.register
def exit_handler():
    """
    Close connections.
    """
    # Clean up sockets
    context.destroy()
    
if __name__ == "__main__":
    main()
