

import socket


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
		
	
	def send_data(self, data: bytearray) -> bool:
		try:
			self.sock.sendall( data )
		except:
			return False

		return True


	def receive_data(self, large_data: bool = False):
		buffer = b''

		if large_data:
			self.sock.settimeout(self.timeout)

		while True:
			try:
				buffer += self.sock.recv(1024)

				if not large_data:
					break

			except socket.timeout:
				break
		
		self.sock.settimeout(None)

		return buffer