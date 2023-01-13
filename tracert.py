import io
import sys
import struct
from socket import *

def ReceivePackages(rec_socket: socket, current_adr, current_name, recieved, tries):
    t = tries
    while not recieved and t > 0:
        try:
            _, current_addresses = rec_socket.recvfrom(580)
            recieved = True
            current_adr = current_addresses[0]
            try:
                current_name = gethostbyaddr(current_adr)[0]
            except error:
                current_name = current_adr
        except error:
            t -= 1
            sys.stdout.write("* ")
    return current_name, current_adr, recieved

class Flusher(io.FileIO):
    def __init__(self, f):
        self.f = f

    def write(self, x):
        self.f.write(x)
        self.f.flush()

def CreateIcmpSocket(port: int) -> socket:
    icmp_socket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
    timeout = struct.pack("ll", 0, 250000)
    icmp_socket.setsockopt(SOL_SOCKET, SO_RCVTIMEO, timeout)
    icmp_socket.bind(("", port))
    return icmp_socket

def CreateUdpSocket(ttl: int) -> socket:
    udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    udp_socket.setsockopt(SOL_IP, IP_TTL, ttl)
    return udp_socket

def TraceRoute(dest_name, tries):
    sys.stdout = Flusher(sys.stdout)
    destination_adr = ""
    try:
        destination_adr = gethostbyname(dest_name)
    except gaierror:
        print(f"No destination with such name: {dest_name}")
        exit(1)
    print(f"Tracing route to {dest_name} ({destination_adr}) with 30 hops limit")

    port = 49152
    hops_limit = 30
    ttl = 1
    while True:
        receiver_socket = CreateIcmpSocket(port)
        sender_socket = CreateUdpSocket(ttl)
        sys.stdout.write(" %2d   " % ttl)
        sender_socket.sendto(bytes("", "utf-8"), (dest_name, port))
        current_adr, current_name, recieved = None, None, False
        current_name, current_adr, recieved = ReceivePackages(receiver_socket, current_name, current_adr, recieved, tries)
        sender_socket.close()
        receiver_socket.close()
        if current_adr is not None:
            current_host = "%s (%s)" % (current_name, current_adr)
        else:
            current_host = ""
        sys.stdout.write("%s\n" % (current_host))
        ttl += 1

        if current_adr == destination_adr or ttl > hops_limit:
            break

args_len = len(sys.argv)
tries = 3
if (args_len == 3):
    tries = int(sys.argv[2])
TraceRoute(sys.argv[1], tries)