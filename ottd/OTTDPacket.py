
import sys, ctypes, logging
from typing import Optional

from . import OTTDEnums

class OTTDPacket(ctypes.Structure):
	logger: logging.Logger = logging.getLogger(__name__)
	logging.basicConfig(level=logging.INFO)

	_pack_ = 1
	_fields_ = [
		("packet_size", ctypes.c_uint16),
		("packet_type", ctypes.c_uint8),
	]

	def __str__(self) -> str:
		return self.to_str()
	
	def __repr__(self) -> str:
		return self.to_str()

	def to_bytes(self):
		return bytearray(self)
	
	@classmethod
	def __to_str__( cls, raw_data, nest = 0 ):
		padding = '  '
		data = f"{padding * nest }{{"

		for field, _ in raw_data._fields_:
			value = getattr(raw_data, field)

			if isinstance(value, ctypes.Array):
				formatted_value = f"[\n"
				for arr_data in value:
					formatted_value += cls.__to_str__(arr_data, nest + 2)
				formatted_value += f"{padding * (nest + 1)}]"
			elif isinstance(value, bool):
				formatted_value = str.lower( str(value) )
			elif isinstance(value, bytes) or isinstance(value, bytearray):
				formatted_value = f"\"{value.decode()}\""
			else:
				formatted_value = value

			data += f"\n{padding * (nest + 1)}\"{field}\": {formatted_value},"
		
		return data + f"\n{padding * nest }}},\n"

	
	def to_str(self):
		return self.__to_str__(self)[:-2]

	@classmethod
	def is_valid_packet(cls, packet: bytearray) -> bool:
		if isinstance(packet, (bytes, bytearray)) and len(packet) >= 2:
			return True
		return False


	@classmethod
	def get_packet_length(cls, packet : bytearray) -> Optional[int]:
		if not cls.is_valid_packet(packet):
			cls.logger.error(f"Invalid packet: {packet}")
			return None
		
		return int.from_bytes(packet[:2], sys.byteorder, signed=False)


	@classmethod
	def get_packet_type(cls, packet : bytearray) -> Optional[int]:
		if not cls.is_valid_packet(packet):
			cls.logger.error(f"Invalid packet: {packet}")
			return None
		
		try:
			return OTTDEnums.PacketAdminType( packet[2] )
		except Exception as e:
			cls.logger.error(f"Failed parsing packet with type: {packet[2]}")
		return None