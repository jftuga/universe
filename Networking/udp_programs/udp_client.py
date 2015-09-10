import socket
import sys

HOST, PORT = "localhost", 9999
data = " ".join(sys.argv[1:])

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
#sock.sendto(bytes(data + "\n","utf8"), (HOST, PORT))
sock.sendto(bytes(data), None, (HOST,PORT))
received = sock.recv(1024)

print("Sent:     %s" % data)
print("Received: %s" % received)

