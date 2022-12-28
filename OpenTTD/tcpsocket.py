
import sys
import socket

import openttd.openttdtypes as ottd

from openttd.packet import Packet

class TCPSocket:
	def __init__(self, ip, port, *, timeout = 1) -> None:
		self.ip = ip
		self.port = port
		self.timeout = timeout

	def connect(self):
		self.disconnect()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.ip, self.port))

	def reconnect(self):
		self.disconnect()
		self.connect()

	def disconnect(self):
		if hasattr(self, 'sock'):
			try:
				self.sock.sendall(b'0')
				self.sock.shutdown(socket.SHUT_RDWR)
			except:
				pass
			
			self.sock.close()

	def send_data(self, data_type: ottd.PacketAdminType, data: bytearray) -> bool:

		_size_ = Packet.int_to_bytes(len(data), 2, separator=b'')
		_type_ = Packet.int_to_bytes(data_type, 1, separator=b'')

		try:
			self.sock.sendall( _size_ + _type_ + data )
		except:
			return False

		return True


	def receive_data(self):
		buffer = b''

		self.sock.settimeout(self.timeout)

		while True:
			try:
				buffer += self.sock.recv(1024)
			except socket.timeout:
				break
		
		self.sock.settimeout(None)

		if len(buffer) < 3:
			return ottd.PacketAdminType.INVALID_ADMIN_PACKET, b''
		
		packet_size = Packet.bytes_to_int(buffer[:2])
		packet_type = ottd.PacketAdminType( buffer[2] )

		return packet_type, buffer[3:]