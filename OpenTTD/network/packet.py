import sys
import socket

import OpenTTD.enums as types

# type + data
# type
# data [ similar to passing raw data to fill the packet]
class Packet(socket.socket):
	def __init__(self, *, packet_type:int = types.INVALID_PACKET, packet_data = b''):

		if packet_type == types.INVALID_PACKET and len(packet_data) > 0:
			packet_type = int(packet_data[2])
			packet_data = packet_data[3:]
		
		self.packet_type = types.PacketAdminType(packet_type)
		self.size = len(packet_data)
		self.data = packet_data
	

	def add_int(self, data: int, byte_count:int, separator: bytes = b'\x00'):
		tmp_data = data.to_bytes(byte_count, sys.byteorder) + separator

		self.size += len(tmp_data)
		self.data += tmp_data


	def add_str(self, data:str, separator: bytes = b'\x00'):
		tmp_data = bytearray(data, "UTF-8") + separator

		self.size += len(tmp_data)
		self.data += tmp_data


	def add_bytes(self, data: bytearray):
		self.size += len(data)
		self.data += data
	
	def get_type(self):
		return types.PacketAdminType(self.packet_type)

	def get_size(self):
		return self.size + 3

	def get_data(self):
		return self.data

	def send_data(self, tcp_socket):
		try:
			data = self.get_size().to_bytes(2, sys.byteorder)
			data += self.packet_type.to_bytes(1, sys.byteorder)
			data += self.data

			tcp_socket.sendall( data )

			return True

		except:
			return False
	

	def receive_data(tcp_socket):
		buffer_size = 1025
		raw_data = b''
		try:
			while True:
				buffer = tcp_socket.recv(buffer_size)
				raw_data += buffer

				if not buffer or len(buffer) < buffer_size :
					break
			
			# a weiredly short message was received
			if len( raw_data ) <= 3:
				return False

			return Packet( packet_data = raw_data )
		except:
			return False



