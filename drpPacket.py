import json

def enum(**enums):
    return type('Enum', (), enums)

PacketType = enum(CONNECTION=1, DATA=2, ACK=3)

# Create Connection Packet
# Creates a DRP packet for initializing connection
# retransmit 	: whether the server must retransmit on timeouts and the client sends ACKs
# bufferSize 	: how many packets the client can hold for ordering
# data 			: the chunk being sent over UDP
def createConnectionPacket(retransmit, bufferSize, data):
	packet = DrpPacket(PacketType.CONNECTION, data)
	packet.addHeaderInformation("retransmit", retransmit)
	packet.addHeaderInformation("bufferSize", bufferSize)
	return packet

# Create Data Packet
# Creates a DRP packet for sending a chunk of data
# sequenceNumber : the sequence number of this specific packet
def createDataPacket(sequenceNumber, data):
	packet = DrpPacket(PacketType.DATA, data)
	packet.addHeaderInformation("sequenceNumber", sequenceNumber)
	return packet

def createAckPacket(sequenceNumber):
	packet = DrpPacket(PacketType.ACK, {})
	packet.addHeaderInformation("")

# Load DRP 
# Parses a json string into a DRP packet object
# string : the json string recieved by the client or server
def loadDrpPacket(string):
	packetObject = json.loads(string)
	packet = DrpPacket(packetObject["body"])

	for key in packetObject["header"]:
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
