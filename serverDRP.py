from socket import *
from drpPacket import *

def main():
	serverPort = 12000
	serverSocket = socket(AF_INET, SOCK_DGRAM)
	serverSocket.bind(('', serverPort))
	data = "STUFF TO SEND"

	print "Server Waiting For Request..."
	message, clientAddress = serverSocket.recvfrom(2048)
	packet = parseDrpPacket(message.decode())
	print "Type: " + str(packet.getHeaderValue("type"))
	print "BufferSize: " + str(packet.getHeaderValue("bufferSize"))

	packetToSend = createDataPacket(ReliabilityType.PEC, 1, data)
	serverSocket.sendto(packetToSend.encode(), clientAddress)
	serverSocket.close()

	"""
	while True:
	    message, clientAddress = serverSocket.recvfrom(2048)
	    modifiedMessage = message.decode().upper()
	    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
	"""

	# packet = createDataPacket(0, "chunk")
	# packet = loadRdpPacket('{"header":{"retransmission":true},"body":"DATA TO SEND"}');
	# print(packet.toString())

if __name__ == "__main__":
	main()
	
