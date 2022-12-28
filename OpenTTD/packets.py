

import openttd.openttdtypes as ottd
import openttd.util as util

#----------------------------------------------
#		ADMIN_PACKET_ADMIN_JOIN
#----------------------------------------------
class PacketAdminJoin:

	def __init__(self, admin_name: str, admin_password: str, app_version: str ) -> None:
		self.admin_password = admin_password
		self.admin_name = admin_name
		self.app_version = app_version
	
	def to_bytes(self) -> bytearray:
		data  = util.int_to_bytes(ottd.PacketAdminType.ADMIN_PACKET_ADMIN_JOIN, 1, separator=b'')
		data += util.str_to_bytes(self.admin_password )
		data += util.str_to_bytes(self.admin_name )
		data += util.str_to_bytes(self.app_version )

		length = util.int_to_bytes(len(data) + 2, 2, separator = b'')

		return length + data


#----------------------------------------------
#		ADMIN_PACKET_SERVER_PROTOCOL
#----------------------------------------------
class PacketServerProtocol:

	def __init__(self, raw_data):

		data_type = ottd.PacketAdminType(raw_data[2])

		if data_type != ottd.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL:
			raise RuntimeError(f"Got {data_type.name} when expecting {ottd.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL.name}")
		
		self.parse_from_bytes( raw_data[3:] )

	def parse_from_bytes(self, raw_data):
		pass


#----------------------------------------------
#		ADMIN_PACKET_SERVER_WELCOME
#----------------------------------------------
class PacketServerWelcome:

	def __init__(self, raw_data):

		data_type = ottd.PacketAdminType(raw_data[2])

		if data_type != ottd.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME:
			raise RuntimeError(f"Got {data_type.name} when expecting {ottd.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME.name}")
		
		self.parse_from_bytes( raw_data[3:] )

	
	def parse_from_bytes(self, raw_data) -> bool:
		index = 0
		length = 0
		
		self.server_name, length = util.get_str_from_bytes( raw_data[index:] )			; index += length
		self.server_version, length = util.get_str_from_bytes(  raw_data[index:] )		; index += length
		self.is_dedicated = util.get_bool_from_bytes( raw_data[index:], 1)				; index += length
		self.map_name, length = util.get_str_from_bytes(  raw_data[index:] )			; index += length
		self.generation_seed, length = util.get_int_from_bytes(  raw_data[index:], 4)	; index += length
		self.landscape, length = util.get_int_from_bytes(  raw_data[index:], 1)			; index += length

		self.start_year, length = util.get_int_from_bytes(  raw_data[index:], 4)		; index += length
		self.start_year = util.ConvertDateToYMD( self.start_year ) 

		map_x, length = util.get_int_from_bytes(  raw_data[index:], 2)	; index += length
		map_y, _ = util.get_int_from_bytes(  raw_data[index:], 2)
		self.map_size = (map_x, map_y)


#----------------------------------------------
#		ADMIN_PACKET_ADMIN_CHAT
#----------------------------------------------
class PacketAdminChat:

	def __init__(self, chat_type, message, *, to_id: int = 0, app: str = '', app_user: str = '', color: int = 0) -> None:
		self.chat_type = chat_type
		self.message = message
		self.to_id = to_id
		self.app = app
		self.app_user = app_user
		self.color = max(0, min(color, 16))		# clamp range 0 - 16

	def is_valid_color( color):
		if not (color & ottd.TextColor.TC_IS_PALETTE_COLOUR):
			return ottd.TextColor.TC_BEGIN <= color and color < ottd.TextColor.TC_END
		
		return False
	
	def __chat__(self):
		_chat_type_ = ottd.CHAT_MAP[self.chat_type][0]
		_dest_type_ = ottd.CHAT_MAP[self.chat_type][1]

		data = util.int_to_bytes(ottd.PacketAdminType.ADMIN_PACKET_ADMIN_CHAT, 1, separator=b'')
		data += util.int_to_bytes(_chat_type_, 1, separator=b'')
		data += util.int_to_bytes(_dest_type_, 1, separator=b'')
		data += util.int_to_bytes(self.to_id, 4, separator=b'')
		data += util.str_to_bytes(self.message)

		return data

	
	def __external_chat__(self):
		data  = util.int_to_bytes(ottd.PacketAdminType.ADMIN_PACKET_ADMIN_EXTERNAL_CHAT, 1, separator=b'')
		data += util.str_to_bytes(self.app)				# source
		data += util.int_to_bytes(self.color, 2, separator=b'')	# color
		data += util.str_to_bytes(self.app_user)						# user
		data += util.str_to_bytes(self.message)

		return data

	def to_bytes(self) -> bytearray:
		data = b''

		if self.chat_type == ottd.CHAT_TYPE.EXTERNAL:
			data += self.__external_chat__()
		else:
			data += self.__chat__()
		
		length = util.int_to_bytes( len(data) + 2, 2, separator=b'')

		return length + data

	



#----------------------------------------------
#		ADMIN_PACKET_ADMIN_POLL
#----------------------------------------------
class PacketAdminPoll:

	def poll(self, update_Type: ottd.AdminUpdateType, tcp_socket, *, extra_data:int = 0xFFFFFFFF):
		data = b''

		data += util.int_to_bytes( update_Type, 1, separator=b'')
		data += util.int_to_bytes( extra_data, 4, separator=b'')

		util.send_data( ottd.PacketAdminType.ADMIN_PACKET_ADMIN_POLL, data, tcp_socket)


#----------------------------------------------
#		DUMMY_PACKET
#----------------------------------------------

class DummyPacket:

	def receive_data(self, tcp_socket) -> tuple:
		self.packet_type, self.data =  util.receive_data(tcp_socket)
		self.packet_type = ottd.PacketAdminType(self.packet_type)
	
	def get_data(self):
		return self.data

	def get_type(self):
		return self.packet_type
		