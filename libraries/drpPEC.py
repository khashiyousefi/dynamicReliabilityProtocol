from drpPacket import *

def receiveBitMap(serverSocket):
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

	return bitMap
