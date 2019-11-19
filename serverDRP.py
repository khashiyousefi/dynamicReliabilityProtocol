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

		serverSocket.sendto(packetToSend.encode(), clientAddress)
		sequenceNumber += 1

	if reliability == ReliabilityType.PEC:
		remainingAttempts = 3
		attempts = 0

		while True:
			message, clientAddress = serverSocket.recvfrom(64000)
			packet = parseDrpPacket(message.decode())
			data = packet.getData()
			bitMap = json.loads(data)
			sentBitMapResponse = False
			index = 0
			bitMapLength = len(bitMap)
			
			for sequenceNumber in bitMap:
				last = bitMapLength == index + 1

				packetToSend = createDataPacket(reliability, sequenceNumber, groupedData[sequenceNumber - 1], fileExtension, last)
				serverSocket.sendto(packetToSend.encode(), clientAddress)
				sentBitMapResponse = True
				index += 1

			if sentBitMapResponse == False:
				packetToSend = createFinPacket()
				serverSocket.sendto(packetToSend.encode(), clientAddress)
				break
			elif remainingAttempts <= 0:
				print 'Error: too many attempts to retransmit missing packets'
				packetToSend = createFinPacket()
				serverSocket.sendto(packetToSend.encode(), clientAddress)
				break
			else:
				remainingAttempts -= 1
				attempts += 1

	print 'PEC: attempts: ' + str(attempts)
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
	bytesPerPacket = args.bytes if args.bytes != None else 2
	return port, args.file, reliability, bytesPerPacket

def getSendingData(filePath):
	if filePath != None:
		try:
			(fileType, encoding) = mimetypes.guess_type(filePath)

			if fileType == 'text/plain':
				file = open(filePath, 'r')
				return file.read()
			else:
				file = open(filePath, 'rb')
				return file.read()
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
	
