from socket import *
from drpPacket import *

def main():
	orderBuffer = []
	recievedBuffer = []
	clientSocket = setupConnection('127.0.0.1', 12000, 10)

	# while True:
	message, clientAddress = clientSocket.recvfrom(2048)
	packet = parseDrpPacket(message.decode())
	data = packet.getData()
	print data
	clientSocket.close()

def setupConnection(serverName, serverPort, bufferSize):
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	packet = createConnectionPacket(bufferSize)
	message = packet.toString()
	clientSocket.sendto(message.encode(), (serverName, serverPort))
	return clientSocket

if __name__ == "__main__":
	main()
