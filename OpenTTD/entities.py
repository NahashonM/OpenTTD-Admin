
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

		self.company, length = Packet.get_int_from_bytes(  raw_data[index:], 1)		; index += length

		_, length = Packet.get_int_from_bytes(  raw_data[index:], 3)		; index += length

		return index


class Company:
	def __init__(self) -> None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):

		index = 0
		length = 0
		
		self.id, length = Packet.get_int_from_bytes( raw_data[index:], 1)					; index += length
		self.name, length = Packet.get_str_from_bytes(  raw_data[index:] )					; index += length
		self.president, length = Packet.get_str_from_bytes(  raw_data[index:] )				; index += length
		self.color, length = Packet.get_int_from_bytes(  raw_data[index:], 1 )				; index += length
		self.has_password, length = Packet.get_bool_from_bytes(  raw_data[index:])			; index += length
		self.start_date, length = Packet.get_int_from_bytes(  raw_data[index:], 4)			; index += length
		self.is_ai, length = Packet.get_bool_from_bytes(  raw_data[index:], 1)				; index += length
		self.quaters_bankrupt, length = Packet.get_int_from_bytes(  raw_data[index:], 1)	; index += length

		self.share_owners = list()
		for i in range(0, types.MAX_COMPANY_SHARE_OWNERS):
			owner, length = Packet.get_int_from_bytes(  raw_data[index:], 1)
			index += length

			self.share_owners.append(owner)

		_, length = Packet.get_int_from_bytes(  raw_data[index:], 3)	; index += length

		return index


class CompanyEconomy:
	def __init__(self) -> None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):

		index = 0
		length = 0

		self.id, length = Packet.get_int_from_bytes( raw_data[index:], 1)					; index += length
		self.money, length = Packet.get_int_from_bytes( raw_data[index:], 8, signed=True)	; index += length
		self.loan, length = Packet.get_int_from_bytes( raw_data[index:], 8, signed=True)	; index += length
		self.income, length = Packet.get_int_from_bytes( raw_data[index:], 8, signed=True)	; index += length
		self.delivered_cargo, length = Packet.get_int_from_bytes( raw_data[index:], 2)		; index += length
		
		self.quarters = list()
		for i in range(0, types.ECONOMY_INFO_QUARTERS):
			company_value, length = Packet.get_int_from_bytes( raw_data[index:], 8, signed=True)				; index += length
			performance_history, length = Packet.get_int_from_bytes( raw_data[index:], 2, signed=True)		; index += length
			delivered_cargo, length = Packet.get_int_from_bytes( raw_data[index:], 2, signed=True)		; index += length

			self.quarters.append( {
				"company_value": company_value, 
				"performance_history": performance_history,
				"delivered_cargo": delivered_cargo
				} )

		_, length = Packet.get_int_from_bytes(  raw_data[index:], 3)	; index += length

		return index


class CompanyStats:
	def __init__(self) -> None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):

		index = 0
		length = 0

		self.id, length = Packet.get_int_from_bytes( raw_data[index:], 1)					; index += length
		
		self.vehicles = dict()
		for i in range(0, types.NetworkVehicleType.NETWORK_VEH_END):
			vehicle = types.NetworkVehicleType(i).name.split('_')[-1]
			count , length = Packet.get_int_from_bytes( raw_data[index:], 2)	; index += length
			
			self.vehicles[vehicle] = count

		self.stations = dict()

		for i in range(0, types.NetworkVehicleType.NETWORK_VEH_END):
			vehicle = types.NetworkVehicleType(i).name.split('_')[-1]
			count , length = Packet.get_int_from_bytes( raw_data[index:], 2)	; index += length
			
			self.stations[vehicle] = count

		_, length = Packet.get_int_from_bytes(  raw_data[index:], 3)	; index += length

		return index

