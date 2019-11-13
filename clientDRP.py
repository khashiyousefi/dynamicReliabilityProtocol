from socket import *
from drpPacket import *

bufferSize = 10
serverName = '127.0.0.1'
serverPort = 12000

orderBuffer = []
recievedBuffer = []

def setupConnection():
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	packet = createConnectionPacket(bufferSize)
	message = packet.toString()
	clientSocket.sendto(message.encode(), (serverName, serverPort))
	return clientSocket

clientSocket = setupConnection()

# while True:
message, clientAddress = clientSocket.recvfrom(2048)
packet = parseDrpPacket(message.decode())
data = packet.getData()
print data
clientSocket.close()


    # clientSocket.sendto(modifiedMessage.encode(), clientAddress)