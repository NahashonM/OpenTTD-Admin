
import openttdtypes as ottd
import util as util

#----------------------------------------------
#		ADMIN_PACKET_ADMIN_PONG	
#----------------------------------------------
class ServerPong:
	def __init__(self, raw_data = None):
		self.parse_from_bytearray( raw_data )

	def parse_from_bytearray(self, raw_data):
		pass


class ServerProtocol:
	def __init__(self, raw_data = None):
		pass

	def parse_from_bytearray(self, raw_data):
		pass


class ServerWelcome:

	def __init__(self):
		pass

	def parse_from_bytearray(self, raw_data) -> bool:
		data_type = ottd.PacketAdminType(raw_data[2])

		if data_type != ottd.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME:
			raise RuntimeError(f"Got {data_type.name} when expecting {ottd.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME.name}")

		index = 3
		length = 0
		
		self.server_name, length = util.get_str_from_bytes( raw_data[index:] )			; index += length
		self.server_version, length = util.get_str_from_bytes(  raw_data[index:] )		; index += length
		self.is_dedicated, length = util.get_bool_from_bytes( raw_data[index:], 1)				; index += length
		self.map_name, length = util.get_str_from_bytes(  raw_data[index:] )			; index += length
		self.generation_seed, length = util.get_int_from_bytes(  raw_data[index:], 4)	; index += length
		self.landscape, length = util.get_int_from_bytes(  raw_data[index:], 1)			; index += length

		self.start_year, length = util.get_int_from_bytes(  raw_data[index:], 4)		; index += length
		self.start_year = util.ConvertDateToYMD( self.start_year ) 

		map_x, length = util.get_int_from_bytes(  raw_data[index:], 2)	; index += length
		map_y, _ = util.get_int_from_bytes(  raw_data[index:], 2)
		self.map_size = (map_x, map_y)



class ServerDate:
	def __init__(self):
		self.YMD = 0
		self.ticks = 0

	def parse_from_bytearray(self, raw_data):
		if raw_data:
			self.ticks = util.bytes_to_int(raw_data[3:])
			self.YMD = util.ConvertDateToYMD(self.ticks)


class Client:
	def __init__(self) -> None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 3
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

		index = 3
		length = 0
		
		self.id, length = util.get_int_from_bytes( raw_data[index:], 1)					; index += length
		self.name, length = util.get_str_from_bytes(  raw_data[index:] )				; index += length
		self.president, length = util.get_str_from_bytes(  raw_data[index:] )			; index += length
		self.color, length = util.get_int_from_bytes(  raw_data[index:], 1 )			; index += length
		self.color = ottd.Color(self.color)
		
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

		index = 3
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
		index = 3
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



class RCONResult:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 3
		length = 0

		self.console_color, length = util.get_int_from_bytes( raw_data[index:], 2)			; index += length
		self.text, length = util.get_str_from_bytes( raw_data[index:])						; index += length

		return index



class RCONEnd:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 3
		self.cmd_text, length = util.get_str_from_bytes( raw_data[index:])		; index += length

		return index


# Whenever a player joins
class ClientJoin:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 3; length = 0
		self.client_id, length = util.get_int_from_bytes( raw_data[index:], 4)		; index += length
		return index


# Whenever a player leaves
class ClientQuit:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 3; length = 0
		self.client_id, length = util.get_int_from_bytes( raw_data[index:], 4)		; index += length
		return index


# Whenever a player switches teams
class ClientUpdate:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 3; length = 0

		self.client_id, length = util.get_int_from_bytes( raw_data[index:], 4)		; index += length
		self.client_name, length = util.get_str_from_bytes( raw_data[index:])		; index += length
		self.client_playas, length = util.get_int_from_bytes( raw_data[index:], 1)		; index += length

		return index


# Whenever a player makes an error
class ClientError:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 3; length = 0
		self.client_id, length = util.get_int_from_bytes( raw_data[index:], 4)	; index += length
		self.error, length = util.get_int_from_bytes( raw_data[index:], 1)		; index += length

		self.error = ottd.NetworkErrorCode(self.error)
		return index


# Whenever a company is created
class CompanyNew:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 3; length = 0
		self.company_id, length = util.get_int_from_bytes( raw_data[index:], 1)	; index += length
		return index


# Whenever a company's details changes
class CompanyUpdate:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 3; length = 0

		self.company_id, length = util.get_int_from_bytes( raw_data[index:], 1)	; index += length
		return index


# Whenever a company is Removed
class CompanyRemove:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		index = 3; length = 0

		self.company_id, length = util.get_int_from_bytes( raw_data[index:], 1)	; index += length
		self.reason, length = util.get_int_from_bytes( raw_data[index:], 1)	; index += length
		
		self.reason = ottd.AdminCompanyRemoveReason(self.reason)
		return index


class ServerNewGame:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		pass


class ServerShutdown:
	def __init__(self) ->None:
		pass

	def parse_from_bytearray(self, raw_data: bytearray):
		pass