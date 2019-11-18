from socket import *
from libraries.drpPacket import *
import argparse
import sys
import binascii
import mimetypes
import random

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, metavar='', help='server port number')
parser.add_argument('-f', '--file', type=str, metavar='', help='file to send')
parser.add_argument('-r', '--reliability', type=int, metavar='', help='reliability type <CONNECTION=1, DATA=2, ACK=3>')
parser.add_argument('-b', '--bytes', type=int, metavar='', help='bytes per DRP packet')
args = parser.parse_args()

def main():
	# Variables
	sequenceNumber = 1

	# Initialize the Server
	port, filePath, reliability, bytesPerPacket = readCommandArguments()
	data = getSendingData(filePath)
	fileExtension = getFileExtension(filePath)	
	serverSocket = setupServer(port)
	groupedData = groupPacketData(data, bytesPerPacket)
	length = len(groupedData)

	# Wait for Client to connect
	message, clientAddress = serverSocket.recvfrom(2048)
	packet = parseDrpPacket(message.decode())
	clientBufferSize = packet.getHeaderValue("bufferSize")

	# Send data packets
	for packetBytes in groupedData:
		last = length == sequenceNumber
		packetToSend = createDataPacket(reliability, sequenceNumber, packetBytes, fileExtension, last)

		if sequenceNumber == 3:
			serverSocket.sendto(packetToSend.encode(), clientAddress)
		sequenceNumber += 1

	if reliability == ReliabilityType.PEC:
		attempts = 3

		while True:
			message, clientAddress = serverSocket.recvfrom(2048)
			packet = parseDrpPacket(message.decode())
			data = packet.getData()
			bitMap = json.loads(data)
			sentBitMapResponse = False
			print bitMap
			
			for index in range(0, length):
				if bitMap[index] == 0:
					packetToSend = createDataPacket(reliability, index + 1, groupedData[index], fileExtension, False)
					serverSocket.sendto(packetToSend.encode(), clientAddress)
					sentBitMapResponse = True

			if sentBitMapResponse == True:
				packetToSend = createFinPacket()
				serverSocket.sendto(packetToSend.encode(), clientAddress)
				break
			elif attempts <= 0:
				print 'Error: too many attempts to retransmit missing packets'
				packetToSend = createFinPacket()
				serverSocket.sendto(packetToSend.encode(), clientAddress)
				break
			else:
				attempts -= 1

	serverSocket.close()

def setupServer(port):
	serverSocket = socket(AF_INET, SOCK_DGRAM)
	serverSocket.bind(('', port))
	return serverSocket

def readCommandArguments():
	port = args.port if args.port != None else 12000

	if args.reliability != None and (args.reliability < 1 or args.reliability > 2):
		print "Error: reliability must be: <CONNECTION=1, DATA=2, ACK=3>"
		sys.exit()

	reliability = args.reliability if args.reliability != None else 1
	bytesPerPacket = args.bytes if args.bytes != None else 4
	return port, args.file, reliability, bytesPerPacket

def getSendingData(filePath):
	if filePath != None:
		try:
			file = open(filePath, "r")
			(fileType, encoding) = mimetypes.guess_type(filePath)

			if fileType == 'text/plain':
				return file.read()
			else:
				return binascii.hexlify(file.read())
		except IOError:
			print "Error: could not open file " + filePath
			sys.exit()

	return "Data to send"

def groupPacketData(data, bytesPerPacket):
	groups = []

	while len(data) > bytesPerPacket:
		group = data[:bytesPerPacket]
		groups.append(group)
		data = data[bytesPerPacket:]

	groups.append(data)
	return groups

def getFileExtension(filePath):
	if filePath != None:
		filePathTokens = filePath.split('.')
		return filePathTokens[len(filePathTokens) - 1]

	return 'txt'

if __name__ == "__main__":
	main()
	
