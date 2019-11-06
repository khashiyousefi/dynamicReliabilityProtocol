from socket import *
from drpPacket import * 

"""
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
data = "STUFF TO SEND"

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode().upper()
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
"""

packet = createDataPacket(0, "chunk")
# packet = loadRdpPacket('{"header":{"retransmission":true},"body":"DATA TO SEND"}');
print(packet.toString())
