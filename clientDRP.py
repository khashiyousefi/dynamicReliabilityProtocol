from socket import *
from libraries.drpPacket import *
import argparse
import sys

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
		ldata = packet.getLData()

		if not missingPackets and receivedNumber - lastReceived > 1:
			missingPackets = True

		if bitMapSent == True or receivedNumber <= lastReceived:
			recievedBuffer, bitMap = updatePacketData(recievedBuffer, data, bitMap, receivedNumber)
		else:
			recievedBuffer, bitMap = storePacketData(reliability, recievedBuffer, data, ldata, bitMap, lastReceived, receivedNumber)

		lastReceived = receivedNumber

		if reliability == ReliabilityType.RETRANSMISSION or packet.getHeaderValue('last') == True:
			ack = createAckPacket()
			clientSocket.sendto(ack.encode(), (ip, port))

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
		lastData = None

		if fileExtension == 'txt':
			file = open(outputPath, 'w')

			for data in recievedBuffer:
				if data == None and reliability > 0:
					data = lastData
				elif data == None:
					data = ''

				file.write(binascii.unhexlify(data))
				lastData = data
		else:
			file = open(outputPath, 'wb')
			
			for data in recievedBuffer:
				if data == None and reliability > 0:
					data = lastData
				elif data == None:
					data = ''

				file.write(binascii.unhexlify(data))
				lastData = data
	
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

	try:
		socket.sendto(message.encode(), (serverName, serverPort))
	except:
		print 'Error: too many files dropped, exceeding maximum size of bitmap 128000 bits'
		sys.exit()

def storePacketData(reliability, recievedBuffer, data, ldata, bitMap, lastReceived, receivedNumber):
	while receivedNumber - lastReceived > 1:
		lastReceived = lastReceived + 1
		bitMap.append(lastReceived)

		if reliability == ReliabilityType.FEC:
			recievedBuffer.append(ldata)
		else:
			recievedBuffer.append(None)	

	recievedBuffer.append(data)
	return recievedBuffer, bitMap

def updatePacketData(recievedBuffer, data, bitMap, receivedNumber):
	bitMap.remove(receivedNumber)
	recievedBuffer[receivedNumber - 1] = data

	return recievedBuffer, bitMap

if __name__ == "__main__":
	main()
