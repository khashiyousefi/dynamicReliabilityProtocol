import unittest
from libraries.drpPacket import *

class TestDrpPacket(unittest.TestCase):
	TEST_BUFFER_SIZE = 10
	TEST_SEQUENCE_NUMBER = 1
	TEST_DATA = "Test_Data"

	def test_createConnectionPacket(self):
		packet = createConnectionPacket(self.TEST_BUFFER_SIZE)
		self.assertEqual(packet.getHeaderValue("type"), PacketType.CONNECTION)
		self.assertEqual(packet.getHeaderValue("bufferSize"), self.TEST_BUFFER_SIZE)

	def test_createDataPacket(self):
		packet = createDataPacket(ReliabilityType.PEC, self.TEST_SEQUENCE_NUMBER, self.TEST_DATA)
		self.assertEqual(packet.getHeaderValue("type"), PacketType.DATA)
		self.assertEqual(packet.getHeaderValue("sequenceNumber"), self.TEST_SEQUENCE_NUMBER)
		self.assertFalse(packet.getHeaderValue("last"))
		self.assertEqual(packet.getData(), self.TEST_DATA)

	def test_createAckPacket(self):
		packet = createAckPacket(self.TEST_SEQUENCE_NUMBER)
		self.assertEqual(packet.getHeaderValue("type"), PacketType.ACK)
		self.assertEqual(packet.getHeaderValue("sequenceNumber"), self.TEST_SEQUENCE_NUMBER)

	def test_parseConnectionDrpPacket(self):
		packet = parseDrpPacket('{"header":{"type":1,"reliability":1},"body":{}}')
		self.assertEqual(packet.getHeaderValue("type"), PacketType.CONNECTION)
		self.assertEqual(packet.getHeaderValue("reliability"), ReliabilityType.RETRANSMISSION)

	def test_parseDataPacket(self):
		packet = parseDrpPacket('{"header":{"type":2,"sequenceNumber":1},"body":"Test_Data"}')
		self.assertEqual(packet.getHeaderValue("type"), PacketType.DATA)
		self.assertEqual(packet.getHeaderValue("sequenceNumber"), self.TEST_SEQUENCE_NUMBER)
		self.assertEqual(packet.getData(), self.TEST_DATA)

	def test_parseAckPacket(self):
		packet = parseDrpPacket('{"header":{"type":3,"sequenceNumber":1},"body":{}}')
		self.assertEqual(packet.getHeaderValue("type"), PacketType.ACK)
		self.assertEqual(packet.getHeaderValue("sequenceNumber"), self.TEST_SEQUENCE_NUMBER)
		
if __name__ == "__main__":
	unittest.main()
