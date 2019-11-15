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
	bytesPerPacket = 3

	message, clientAddress = serverSocket.recvfrom(2048)
	packet = parseDrpPacket(message.decode())
	clientBufferSize = packet.getHeaderValue("bufferSize")
	groupedData = groupPacketData(data, bytesPerPacket)
	length = len(groupedData)

	for packetBytes in groupedData:
		last = length == sequenceNumber
		packetToSend = createDataPacket(ReliabilityType.PEC, sequenceNumber, packetBytes, last)
		serverSocket.sendto(packetToSend.encode(), clientAddress)
		sequenceNumber += 1

	serverSocket.close()

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
			return bytearray(file.read())
		except IOError:
			print "Error: could not open file " + filePath
			sys.exit()

	return bytearray("Data to send")

def groupPacketData(data, bytesPerPacket):
	groups = []

	while len(data) > bytesPerPacket:
		group = data[:bytesPerPacket]
		groups.append(group)
		data = data[bytesPerPacket:]

	groups.append(data)
	return groups

if __name__ == "__main__":
	main()
	
