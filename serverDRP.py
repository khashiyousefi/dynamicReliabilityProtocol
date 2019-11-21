from socket import *
from libraries.drpPacket import *
import argparse
import sys
import binascii
import mimetypes
import random

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ip', type=str, metavar='', help='server ip address')
parser.add_argument('-p', '--port', type=int, metavar='', help='server port number')
parser.add_argument('-f', '--file', type=str, metavar='', help='file to send')
parser.add_argument('-l', '--lfile', type=str, metavar='', help='low quality file to send <required when using FEC>')
parser.add_argument('-r', '--reliability', type=int, metavar='', help='reliability type <UDP=0, RETRANSMISSION=1, PEC=2, FEC=3>')
parser.add_argument('-b', '--bytes', type=int, metavar='', help='bytes per DRP packet')
parser.add_argument('-t', '--timeout', type=int, metavar='', help='milliseconds before a timeout')
parser.add_argument('-a', '--attempts', type=int, metavar='', help='number of attempts for retransmission or bitmap transmissions')
parser.add_argument('-d', '--droprate', type=int, metavar='', help='rate in which UDP will drop packets <0 - 100> where 0=no drops and 100=every packet drops')
args = parser.parse_args()


def main():
	# Variables
	sequenceNumber = 1

	# Initialize the Server
	ip, port, filePath, lfilePath, reliability, bytesPerPacket, timeout, attempts, droprate = readCommandArguments()

	if reliability == ReliabilityType.FEC and (filePath == None or lfilePath == None):
		print 'Error: must include both a normal file using -f and low quality file using -l'
		sys.exit()

	data, ldata = getSendingData(filePath, lfilePath)

	if reliability != ReliabilityType.FEC:
		ldata = None # just ignore low quality data if someone passed it in when they didnt need to

	fileExtension = getFileExtension(filePath)	
	serverSocket = setupServer(ip, port)
	groupedData, lgroupedData = groupPacketData(data, ldata, bytesPerPacket)
	length = len(groupedData)

	# Wait for Client to connect
	message, clientAddress = serverSocket.recvfrom(2048)
	packet = parseDrpPacket(message.decode())
	clientBufferSize = packet.getHeaderValue("bufferSize")

	# Send data packets
	for packetBytes in groupedData:
		last = length == sequenceNumber

		if reliability == ReliabilityType.FEC:
			lowerBytes = lgroupedData[sequenceNumber - 2] if sequenceNumber > 1 else ''
			packetToSend = createFecDataPacket(reliability, sequenceNumber, packetBytes, lowerBytes, fileExtension, last)
		else:
			packetToSend = createDataPacket(reliability, sequenceNumber, packetBytes, fileExtension, last)

		if random.random() > droprate:
			serverSocket.sendto(packetToSend.encode(), clientAddress)

		sequenceNumber += 1

		if reliability == ReliabilityType.RETRANSMISSION or last:
			currentAttempt = 0

			while True:
				try:
					serverSocket.settimeout(timeout)
					message, clientAddress = serverSocket.recvfrom(2048)
					break
				except:
					currentAttempt += 1

					if currentAttempt > attempts:
						print 'Error: retransmission of the same packet occured more than ' + str(attempts) + ' times'
						sys.exit()

					if random.random() > droprate:
						serverSocket.sendto(packetToSend.encode(), clientAddress)

	if reliability == ReliabilityType.PEC:
		remainingAttempts = attempts
		currentAttempt = 0

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

				if last:
					currentAttempt = 0

					while True:
						try:
							serverSocket.settimeout(timeout)
							message, clientAddress = serverSocket.recvfrom(2048)
							break
						except:
							currentAttempt += 1

							if currentAttempt > attempts:
								print 'Error: retransmission of the same packet occured more than ' + str(attempts) + ' times'
								sys.exit()

							if random.random() > droprate:
								serverSocket.sendto(packetToSend.encode(), clientAddress)

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
				currentAttempt += 1

		print 'PEC: attempts: ' + str(currentAttempt)
	
	serverSocket.close()

def setupServer(ip, port):
	serverSocket = socket(AF_INET, SOCK_DGRAM)
	serverSocket.bind((ip, port))
	return serverSocket

def readCommandArguments():
	ip = args.ip if args.ip != None else ''
	port = args.port if args.port != None else 12000

	if args.reliability != None and (args.reliability < 0 or args.reliability > 3):
		print "Error: reliability must be: <UDP=0, RETRANSMISSION=1, PEC=2, FEC=3>"
		sys.exit()

	reliability = args.reliability if args.reliability != None else 1
	bytesPerPacket = args.bytes if args.bytes != None else 2
	timeout = (args.timeout / 1000.0) if args.timeout != None else 0.01
	attempts = args.attempts if args.attempts != None else 3
	droprate = args.droprate if args.droprate != None else 0

	if bytesPerPacket <= 0:
		print "Error: bytes per packet must be > 0"
		sys.exit()

	if timeout <= 0:
		print timeout
		print "Error: timeout must be > 0"
		sys.exit()

	if attempts <= 0:
		print "Error: attempts must be > 0"
		sys.exit()

	if droprate < 0 or droprate > 100:
		print "Error: droprate must be between 0 and 100"
		sys.exit()

	droprate = droprate / 100.0
	return ip, port, args.file, args.lfile, reliability, bytesPerPacket, timeout, attempts, droprate

def getSendingData(filePath, lfilePath):
	if filePath != None:
		try:
			ldata = None
			(fileType, encoding) = mimetypes.guess_type(filePath)

			if fileType == 'text/plain':
				file = open(filePath, 'r')

				if lfilePath != None:
					lfile = open(lfilePath, 'r')
					ldata = lfile.read()

				return file.read(), ldata
			else:
				file = open(filePath, 'rb')

				if lfilePath != None:
					lfile = open(lfilePath, 'r')
					ldata = lfile.read()

				return file.read(), ldata
		except IOError:
			print "Error: could not open file " + filePath
			sys.exit()

	return "Data to send"

def groupPacketData(data, ldata, bytesPerPacket):
	groups = []
	lgroups = []

	while len(data) > bytesPerPacket:
		group = data[:bytesPerPacket]
		groups.append(group)
		data = data[bytesPerPacket:]

	groups.append(data)

	if ldata != None:
		while len(ldata) > bytesPerPacket:
			group = ldata[:bytesPerPacket]
			lgroups.append(group)
			ldata = ldata[bytesPerPacket:]

		lgroups.append(ldata)

	return groups, lgroups

def getFileExtension(filePath):
	if filePath != None:
		filePathTokens = filePath.split('.')
		return filePathTokens[len(filePathTokens) - 1]

	return 'txt'

if __name__ == "__main__":
	main()
	
