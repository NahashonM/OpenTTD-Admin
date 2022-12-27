
import OpenTTD.enums as types

from OpenTTD.date import Date
from OpenTTD.network.packet import Packet


class Client:
	def __init__(self) -> None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 0
		length = 0
		
		self.id, length = Packet.get_int_from_bytes( raw_data[index:], 4)	; index += length
		self.address, length = Packet.get_str_from_bytes(  raw_data[index:] )		; index += length
		self.name, length = Packet.get_str_from_bytes(  raw_data[index:] )			; index += length
		self.lang, length = Packet.get_int_from_bytes(  raw_data[index:], 1 )		; index += length
		self.join_date, length = Packet.get_int_from_bytes(  raw_data[index:], 4)	; index += length
		self.join_date = Date.ConvertDateToYMD(self.join_date)

		self.playas, length = Packet.get_int_from_bytes(  raw_data[index:], 4)

		return index + length

class Company:
	def __init__(self) -> None:

		self.name =''
		self.is_protected = False

		self.start_year = 0
		self.president =''
		self.color = ''

		self.loan = 0
		self.value = 0
		self.bank_balance = 0
