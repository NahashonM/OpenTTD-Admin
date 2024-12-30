
import ctypes


class BasePacket(ctypes.Structure):
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
	
	def to_str(self):
		data = '{'

		for field, _ in self._fields_:
			value = getattr(self, field)

			if isinstance(value, ctypes.Array):
				value = f"{[x for x in value]}"
			
			elif isinstance(value, bool):
				value = str.lower( str(value) )
			
			elif isinstance(value, bytes) or isinstance(value, bytearray):
				value = f"\"{value.decode()}\""

			data += f"\"{field}\":{value},"
		
		if data[-1] == ',':
			data = data[:-1]
			
		return data + '}'




