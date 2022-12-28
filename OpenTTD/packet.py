
import sys

class Packet:
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

