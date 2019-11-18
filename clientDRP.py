from socket import *
from libraries.drpPacket import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ip', type=str, metavar='', help='server IP address')
parser.add_argument('-p', '--port', type=int, metavar='', help='server port number')
parser.add_argument('-b', '--buffer', type=int, metavar='', help='client buffer size')
parser.add_argument('-o', '--output', type=str, metavar='', help='output path')
args = parser.parse_args()

def main():
	ip, port, bufferSize, outputPath = readCommandArguments()
	orderBuffer = []
	recievedBuffer = []
	bitMap = []
	lastReceived = 0
	bitMapSent = False
	missingPackets = False
	clientSocket = setupConnection(ip, port, bufferSize)
	fileExtension = 'txt'

	while True:
		message, clientAddress = clientSocket.recvfrom(2048)
		packet = parseDrpPacket(message.decode())

		# Received a fin packet - told to close connection
		if packet.getHeaderValue('type') == PacketType.ACK and packet.getHeaderValue('last') == True:
			break;

		reliability = packet.getHeaderValue('reliability')
		receivedNumber = packet.getHeaderValue('sequenceNumber')
		fileExtension = packet.getHeaderValue('fileExtension')
		data = packet.getData()

		if not missingPackets and receivedNumber - lastReceived > 1:
			missingPackets = True

		if bitMapSent == True:
			recievedBuffer, bitMap = updatePacketData(recievedBuffer, data, bitMap, receivedNumber)
		else:
			recievedBuffer, bitMap = storePacketData(recievedBuffer, data, bitMap, lastReceived, receivedNumber)

		lastReceived = receivedNumber

		if packet.getHeaderValue('last') == True:
			if reliability == ReliabilityType.PEC:
				sendBitMap(clientSocket, ip, port, bitMap)
				bitMapSent = True
				lastReceived = 0

				if missingPackets == False:
					break;
			else:
				break;

	clientSocket.close()

	if outputPath != None:
		file = open(outputPath, 'w')
		counter = 0

		for data in recievedBuffer:
			file.write(data)

			if fileExtension == 'txt':
				continue
			elif counter >= 7:
				counter = 0
				file.write('\n')
			else:
				file.write(' ')
				counter += 1
	
		file.close()
	else:
		print recievedBuffer

def readCommandArguments():
	ip = args.ip if args.ip != None else '127.0.0.1'
	port = args.port if args.port != None else 12000
	bufferSize = args.buffer if args.buffer != None else 10
	return ip, port, bufferSize, args.output

def setupConnection(serverName, serverPort, bufferSize):
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	packet = createConnectionPacket(bufferSize)
	message = packet.toString()
	clientSocket.sendto(message.encode(), (serverName, serverPort))
	return clientSocket

def sendBitMap(socket, serverName, serverPort, bitMap):
	packet = createBitMapPacket(bitMap)
	message = packet.toString()
	socket.sendto(message.encode(), (serverName, serverPort))

def storePacketData(recievedBuffer, data, bitMap, lastReceived, receivedNumber):
	while receivedNumber - lastReceived > 1:
		bitMap.append(0)
		recievedBuffer.append(None)
		lastReceived = lastReceived + 1

	recievedBuffer.append(data)
	bitMap.append(1)

	return recievedBuffer, bitMap

def updatePacketData(recievedBuffer, data, bitMap, receivedNumber):
	bitMap[receivedNumber - 1] = 1
	recievedBuffer[receivedNumber - 1] = data

	return recievedBuffer, bitMap

if __name__ == "__main__":
	main()
