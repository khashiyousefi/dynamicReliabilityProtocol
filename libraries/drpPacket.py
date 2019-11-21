import json
import binascii

def enum(**enums):
    return type('Enum', (), enums)

PacketType = enum(CONNECTION=1, DATA=2, ACK=3)
ReliabilityType = enum(UDP=0, RETRANSMISSION=1, PEC=2, FEC=3)

# Create Connection Packet
# Creates a DRP packet for initializing connection from the receiver
# bufferSize 	: how many packets the client can hold for ordering
def createConnectionPacket(bufferSize):
	packet = DrpPacket(PacketType.CONNECTION, {})
	packet.addHeaderInformation("bufferSize", bufferSize)
	return packet

# Create Data Packet
# Creates a DRP packet for sending a chunk of data
# reliability 	 : type of reliability 
# sequenceNumber : the sequence number of this specific packet
# fileExtension  : the extension of the file
# data 			 : the chunk being sent over UDP
# last			 : whether this is the last data packet or not
def createDataPacket(reliability, sequenceNumber, data, fileExtension, last=False):
	packet = DrpPacket(PacketType.DATA, data)
	packet.addHeaderInformation("reliability", reliability)
	packet.addHeaderInformation("sequenceNumber", sequenceNumber)
	packet.addHeaderInformation("fileExtension", fileExtension)
	packet.addHeaderInformation("last", last)
	return packet

# Create FEC Data Packet
# Creates an FEC packet for sending a chunk of data
# reliability 	 : type of reliability 
# sequenceNumber : the sequence number of this specific packet
# fileExtension  : the extension of the file
# data 			 : the chunk being sent over UDP
# ldata			 : the lower quality chunk from the previous packet
# last			 : whether this is the last data packet or not
def createFecDataPacket(reliability, sequenceNumber, data, ldata, fileExtension, last=False):
	packet = DrpPacket(PacketType.DATA, data, ldata)
	packet.addHeaderInformation("reliability", reliability)
	packet.addHeaderInformation("sequenceNumber", sequenceNumber)
	packet.addHeaderInformation("fileExtension", fileExtension)
	packet.addHeaderInformation("last", last)
	return packet

# Create Ack Packet
# Creates a DRP packet for acknowledging that a data packet was received
# sequenceNumber : the sequence number of the packet received 
def createAckPacket():
	packet = DrpPacket(PacketType.ACK, {})
	return packet

# Create BitMap Packet
# Creates a DRP packet for responding with a bitmap of missing packets
# bitMap : the bitmap of missing packets
def createBitMapPacket(bitMap):
	packet = DrpPacket(PacketType.ACK, bitMap)
	return packet

# Create Fin Packet
# Creates a DRP packet for notifying the connection will be closed
def createFinPacket():
	packet = DrpPacket(PacketType.ACK, {})
	packet.addHeaderInformation("last", True)
	return packet

# Parse DRP 
# Parses a json string into a DRP packet object
# string : the json string recieved by the client or server
def parseDrpPacket(string):
	packetObject = json.loads(string)
	packet = DrpPacket(packetObject["header"]["type"], packetObject["body"], packetObject["lbody"])

	for key in packetObject["header"]:
		if key != "type":
			packet.addHeaderInformation(key, packetObject["header"][key])

	return packet

class DrpPacket:
	def __init__(self, packetType, data, ldata=''):
		if type(data) == str:
			data = binascii.hexlify(data)

		if type(ldata) == str:
			ldata = binascii.hexlify(ldata)

		self.packet = {
			"header": {
				"type": packetType
			},
			"body": str(data),
			"lbody": str(ldata)
		}

	def addHeaderInformation(self, key, value):
		self.packet["header"][key] = value

	def toString(self):
		return json.dumps(self.packet)

	def encode(self):
		packetString = self.toString()
		return packetString.encode()

	def getHeaderValue(self, key):
		return self.packet["header"][key]

	def getData(self):
		return self.packet["body"]

	def getLData(self):
		return self.packet["lbody"]
