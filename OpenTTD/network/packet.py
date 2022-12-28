
import sys
import socket
import OpenTTD.enums as types


class Packet(socket.socket):
	#---------------------------------
	# type conversion
	#---------------------------------
	def int_to_bytes(int_value: int, byte_count:int, separator: bytes = b'\x00') -> bytearray:
		tmp_data = int_value.to_bytes(byte_count, sys.byteorder) + separator
		return tmp_data

	def str_to_bytes(str_value:str, separator: bytes = b'\x00') -> bytearray:
		tmp_data = bytearray(str_value, "UTF-8") + separator
		return tmp_data

	
	def bytes_to_int(byte_value: bytearray, signed=False) -> int:
		return int.from_bytes(byte_value, sys.byteorder, signed=signed)
	
	def bytes_to_str(byte_value: bytearray) -> str:
		return byte_value.decode()
	
	def bytes_to_bool(byte_value: bytearray) -> bool:
		return bool.from_bytes(byte_value, byteorder=sys.byteorder)

	#---------------------------------
	# type parse
	#---------------------------------
	def get_int_from_bytes(byte_value: bytearray, int_size: int, *, signed=False):
		int_value = Packet.bytes_to_int( byte_value[: int_size], signed=signed )
		return int_value, int_size

	def get_bool_from_bytes(byte_value: bytearray, bool_size: int = 1):
		bool_value = Packet.bytes_to_bool( byte_value[: bool_size] )
		return bool_value, bool_size

	def get_str_from_bytes(byte_value: bytearray) -> bool:
		str_value = Packet.bytes_to_str( byte_value[: byte_value.index(b'\x00')] )
		return str_value, len(str_value) + 1

	#---------------------------------
	# Network get fetch
	#---------------------------------

	def send_data(packet_type: types.PacketAdminType, data: bytearray, tcp_socket: socket.socket) -> bool:
		try:
			packet_size = (len(data) + 3).to_bytes(2, sys.byteorder)
			packet_type = types.PacketAdminType(packet_type).to_bytes(1, sys.byteorder)

			data = packet_size + packet_type + data

			tcp_socket.sendall( data )

			return True
		except:
			return False
	

	def receive_data(tcp_socket) -> tuple:
		
		buffer = b''
		try:
			while True:

				buffer += tcp_socket.recv(1024)

				size_fetched = len(buffer)
				message_size = Packet.bytes_to_int(buffer[:2])

				print( message_size, size_fetched, buffer)

				if size_fetched == 0 or size_fetched >=  message_size:
					break

			packet_type = types.PacketAdminType( buffer[2] )

			return packet_type, buffer[3:]
		except Exception as e:
			print(e)
			return 0, b''



