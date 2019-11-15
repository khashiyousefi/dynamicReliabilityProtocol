from socket import *
from drpPacket import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ip', type=str, metavar='', help='server IP address')
parser.add_argument('-p', '--port', type=int, metavar='', help='server port number')
parser.add_argument('-b', '--buffer', type=int, metavar='', help='client buffer size')
args = parser.parse_args()

def main():
	ip, port, bufferSize = readCommandArguments()
	orderBuffer = []
	recievedBuffer = []
	clientSocket = setupConnection(ip, port, bufferSize)

	while True:
		message, clientAddress = clientSocket.recvfrom(2048)
		packet = parseDrpPacket(message.decode())
		data = packet.getData()
		recievedBuffer.append(data)

		if packet.getHeaderValue("last") == True:
			break;

	print(str(recievedBuffer))

	clientSocket.close()

def readCommandArguments():
	ip = args.ip if args.ip != None else '127.0.0.1'
	port = args.port if args.port != None else 12000
	bufferSize = args.buffer if args.buffer != None else 10
	return ip, port, bufferSize

def setupConnection(serverName, serverPort, bufferSize):
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	packet = createConnectionPacket(bufferSize)
	message = packet.toString()
	clientSocket.sendto(message.encode(), (serverName, serverPort))
	return clientSocket

if __name__ == "__main__":
	main()
