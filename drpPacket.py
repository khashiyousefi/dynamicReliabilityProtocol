import json

def enum(**enums):
    return type('Enum', (), enums)

PacketType = enum(CONNECTION=1, DATA=2, ACK=3)
ReliabilityType = enum(RETRANSMISSION=1, PEC=2, FEC=3)

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
# data 			 : the chunk being sent over UDP
# last			 : whether this is the last data packet or not
def createDataPacket(reliability, sequenceNumber, data, last=False):
	packet = DrpPacket(PacketType.DATA, data)
	packet.addHeaderInformation("reliability", reliability)
	packet.addHeaderInformation("sequenceNumber", sequenceNumber)
	packet.addHeaderInformation("last", last)
	return packet

# Create Ack Packet
# Creates a DRP packet for acknowledging that a data packet was received
# sequenceNumber : the sequence number of the packet received 
def createAckPacket(sequenceNumber):
	packet = DrpPacket(PacketType.ACK, {})
	packet.addHeaderInformation("sequenceNumber", sequenceNumber)
	return packet

# Parse DRP 
# Parses a json string into a DRP packet object
# string : the json string recieved by the client or server
def parseDrpPacket(string):
	packetObject = json.loads(string)
	packet = DrpPacket(packetObject["header"]["type"], packetObject["body"])

	for key in packetObject["header"]:
		if key != "type":
			packet.addHeaderInformation(key, packetObject["header"][key])

	return packet

class DrpPacket:
	def __init__(self, packetType, data):
		self.packet = {
			"header": {
				"type": packetType
			},
			"body": data
		}

	def addHeaderInformation(self, key, value):
		self.packet["header"][key] = value

	def toString(self):
		return json.dumps(self.packet)

	def encode(self):
		return self.toString().encode()

	def getHeaderValue(self, key):
		return self.packet["header"][key]

	def getData(self):
		return self.packet["body"]
