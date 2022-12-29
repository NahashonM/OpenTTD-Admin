

import socket
import threading 

# Handles all network sends and gets
# Uses thread locks to prevent sync chaos in a multithreading scenario
# Every sending thread acquires lock and releases when a receive is complete
#
# For use in multiple threads, recommendations are to create a new instance.
class TCPSocket:
	def __init__(self, ip, port, *, timeout = 0.3) -> None:
		self.ip = ip
		self.port = port
		self.timeout = timeout
		
		self.lock = threading.Lock()


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

				self.lock.release()
			except:
				pass
			
			self.sock.close()
		
	

	def is_locked(self) -> bool:
		return self.lock.locked()
		
	
	def send_data(self, data: bytearray) -> bool:

		self.lock.acquire()

		try:
			self.sock.sendall( data )
		except:
			return False

		return True
	

	def peek(self, num_bytes: int = 3):

		if not self.lock.locked(): 
			raise RuntimeError ("Attempt to use socket without Lock")
		
		data = b''
		self.sock.settimeout(self.timeout)

		try:
			data = self.sock.recv( num_bytes, socket.MSG_PEEK )
		except socket.timeout:
				pass

		self.sock.settimeout(None)
		return data


	def receive_data(self, buffer_size, release_lock = True):

		if not self.lock.locked():
			raise RuntimeError ("Attempt to use socket without Lock")

		buffer = self.sock.recv(buffer_size)
		
		if release_lock: 
			self.lock.release()

		return buffer