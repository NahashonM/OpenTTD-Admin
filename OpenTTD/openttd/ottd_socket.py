
import time
import socket
import logging

sklog = logging.getLogger("OTTDSock")

class OttdSocket:
	def __init__(self, server_ip, admin_port, timeout = 0.3) -> None:
		self.ip  = server_ip
		self.port = int(admin_port)

		self.timeout = timeout


	def connect(self):
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((self.ip, self.port))
			self.sock.settimeout(self.timeout)
		except Exception as e:
			sklog.critical(f"Failed to connect to {self.ip}:{self.port}")
			sklog.critical(f"Please Make sure the server is started.\n\t[Exception] {e}\n---------EXITING---------")
			exit(0)


	def disconnect(self):
		if hasattr(self, 'sock'):
			sklog.warning(f"Disconnecting from {self.ip}:{self.port}")
			try:
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
	

	def peek(self,*, num_bytes: int = 3, retries: int= 1):
		data = b''

		try:
			while (retries > 0):
				retries -= 1
				data = self.sock.recv( num_bytes, socket.MSG_PEEK )

				if len(data) == num_bytes:
					break

				time.sleep(0.01)

		except socket.timeout:
				pass

		return data


	def receive_data(self, buffer_size):
		data = b''

		try:
			data = self.sock.recv(buffer_size)
		except socket.timeout:
			pass
		
		return bytearray(data)