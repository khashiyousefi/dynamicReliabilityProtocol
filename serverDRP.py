from socket import *
from drpPacket import *
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, metavar='', help='server port number')
parser.add_argument('-f', '--file', type=str, metavar='', help='file to send')
parser.add_argument('-r', '--reliability', type=int, metavar='', help='reliability type <CONNECTION=1, DATA=2, ACK=3>')
args = parser.parse_args()

def main():
	port, filePath, reliability = readCommandArguments()
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
		packetToSend = createDataPacket(reliability, sequenceNumber, packetBytes, last)

		serverSocket.sendto(packetToSend.encode(), clientAddress)
		sequenceNumber += 1

	if reliability == ReliabilityType.PEC:
		message, clientAddress = serverSocket.recvfrom(2048)
		packet = parseDrpPacket(message.decode())
		data = packet.getData()
		bitMap = json.loads(data)
		sentBitMapResponse = False
		
		for index in range(0, length):
			if bitMap[index] == 0:
				packetToSend = createDataPacket(reliability, index - 1, groupedData[index], False)
				serverSocket.sendto(packetToSend.encode(), clientAddress)
				sentBitMapResponse = True

		if sentBitMapResponse == True:
			packetToSend = createFinPacket()
			serverSocket.sendto(packetToSend.encode(), clientAddress)

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
	return port, args.file, reliability

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
	
