
import openttd.openttdtypes as ottd
import openttd.util as util

class Client:
	def __init__(self) -> None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 0
		length = 0
		
		self.id, length = util.get_int_from_bytes( raw_data[index:], 4)			; index += length
		self.address, length = util.get_str_from_bytes(  raw_data[index:] )		; index += length
		self.name, length = util.get_str_from_bytes(  raw_data[index:] )		; index += length
		self.lang, length = util.get_int_from_bytes(  raw_data[index:], 1 )		; index += length
		self.join_date, length = util.get_int_from_bytes(  raw_data[index:], 4)	; index += length
		self.join_date = util.ConvertDateToYMD(self.join_date)

		self.company, length = util.get_int_from_bytes(  raw_data[index:], 1)	; index += length

		_, length = util.get_int_from_bytes(  raw_data[index:], 3)				; index += length

		return index


class Company:
	def __init__(self) -> None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):

		index = 0
		length = 0
		
		self.id, length = util.get_int_from_bytes( raw_data[index:], 1)					; index += length
		self.name, length = util.get_str_from_bytes(  raw_data[index:] )				; index += length
		self.president, length = util.get_str_from_bytes(  raw_data[index:] )			; index += length
		self.color, length = util.get_int_from_bytes(  raw_data[index:], 1 )			; index += length
		self.has_password, length = util.get_bool_from_bytes(  raw_data[index:])		; index += length
		self.start_date, length = util.get_int_from_bytes(  raw_data[index:], 4)		; index += length
		self.is_ai, length = util.get_bool_from_bytes(  raw_data[index:], 1)			; index += length
		self.quaters_bankrupt, length = util.get_int_from_bytes(  raw_data[index:], 1)	; index += length

		self.share_owners = list()
		for i in range(0, ottd.MAX_COMPANY_SHARE_OWNERS):
			owner, length = util.get_int_from_bytes(  raw_data[index:], 1)
			index += length

			self.share_owners.append(owner)

		_, length = util.get_int_from_bytes(  raw_data[index:], 3)	; index += length

		return index


class CompanyEconomy:
	def __init__(self) -> None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):

		index = 0
		length = 0

		self.id, length = util.get_int_from_bytes( raw_data[index:], 1)						; index += length
		self.money, length = util.get_int_from_bytes( raw_data[index:], 8, signed=True)		; index += length
		self.loan, length = util.get_int_from_bytes( raw_data[index:], 8, signed=True)		; index += length
		self.income, length = util.get_int_from_bytes( raw_data[index:], 8, signed=True)	; index += length
		self.delivered_cargo, length = util.get_int_from_bytes( raw_data[index:], 2)		; index += length
		
		self.quarters = list()
		for i in range(0, ottd.ECONOMY_INFO_QUARTERS):
			company_value, length = util.get_int_from_bytes( raw_data[index:], 8, signed=True)			; index += length
			performance_history, length = util.get_int_from_bytes( raw_data[index:], 2, signed=True)	; index += length
			delivered_cargo, length = util.get_int_from_bytes( raw_data[index:], 2, signed=True)		; index += length

			self.quarters.append( {
				"company_value": company_value, 
				"performance_history": performance_history,
				"delivered_cargo": delivered_cargo
				} )

		_, length = util.get_int_from_bytes(  raw_data[index:], 3)	; index += length

		return index


class CompanyStats:
	def __init__(self) -> None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):

		index = 0
		length = 0

		self.id, length = util.get_int_from_bytes( raw_data[index:], 1)			; index += length
		
		self.vehicles = dict()
		for i in range(0, ottd.NetworkVehicleType.NETWORK_VEH_END):
			vehicle = ottd.NetworkVehicleType(i).name.split('_')[-1]
			count , length = util.get_int_from_bytes( raw_data[index:], 2)		; index += length
			
			self.vehicles[vehicle] = count

		self.stations = dict()

		for i in range(0, ottd.NetworkVehicleType.NETWORK_VEH_END):
			vehicle = ottd.NetworkVehicleType(i).name.split('_')[-1]
			count , length = util.get_int_from_bytes( raw_data[index:], 2)		; index += length
			
			self.stations[vehicle] = count

		_, length = util.get_int_from_bytes(  raw_data[index:], 3)				; index += length

		return index


# class RCONResult:
# 	def __init__(self) ->None:
# 		pass

# 	def parse_from_bytearray(self, raw_data: bytearray):
# 		index = 0
# 		length = 0

# 		self.value, length = util.get_str_from_bytes( raw_data[index:])			; index += length
# 		_, length = util.get_int_from_bytes( raw_data[index:], 5)			; index += length
		
# 		return index


class RCONResult:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 0
		length = 0

		self.value, length = util.get_str_from_bytes( raw_data[index:])			; index += length
		_, length = util.get_int_from_bytes( raw_data[index:], 5)			; index += length
		
		return index
		