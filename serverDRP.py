from socket import *
from drpPacket import *
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, metavar='', help='server port number')
parser.add_argument('-f', '--file', type=str, metavar='', help='file to send')
args = parser.parse_args()

def main():
	port, filePath = readCommandArguments()
	data = getSendingData(filePath)

	serverSocket = setupServer(port)
	sequenceNumber = 1

	message, clientAddress = serverSocket.recvfrom(2048)
	packet = parseDrpPacket(message.decode())
	clientBufferSize = packet.getHeaderValue("bufferSize")

	packetToSend = createDataPacket(ReliabilityType.PEC, sequenceNumber, data)
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

def setupServer(port):
	serverSocket = socket(AF_INET, SOCK_DGRAM)
	serverSocket.bind(('', port))
	return serverSocket

def readCommandArguments():
	port = args.port if args.port != None else 12000
	return port, args.file

def getSendingData(filePath):
	if filePath != None:
		try:
			file = open(filePath, "r")
			return file.read()
		except IOError:
			print "Error: could not open file " + filePath
			sys.exit()

	return "Data to send"

if __name__ == "__main__":
	main()
	
