

import openttdtypes as ottd
import util as util

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
#		ADMIN_PACKET_ADMIN_PING	
#----------------------------------------------
class PacketAdminPing:
	def __init__(self):
		pass
	
	def to_bytes(self):
		data  = util.int_to_bytes( ottd.PacketAdminType.ADMIN_PACKET_ADMIN_PING, 1, separator=b'')
		data += util.int_to_bytes( 0, 4, separator=b'')

		length = util.int_to_bytes( len(data) + 2, 2, separator=b'')
		return length + data


#----------------------------------------------
#		ADMIN_PACKET_ADMIN_QUIT	
#----------------------------------------------
class PacketAdminQuit:
	def __init__(self):
		pass
	
	def to_bytes(self):
		data  = util.int_to_bytes( ottd.PacketAdminType.ADMIN_PACKET_ADMIN_QUIT, 1, separator=b'')

		length = util.int_to_bytes( len(data) + 2, 2, separator=b'')
		return length + data



#----------------------------------------------
#		ADMIN_PACKET_ADMIN_POLL
#----------------------------------------------
class PacketAdminPoll:
	def __init__(self, update_type: ottd.AdminUpdateType, *, extra_data:int = 0xFFFFFFFF):
		self.update_type = update_type
		self.extra_data = extra_data
	
	def to_bytes(self):
		data  = util.int_to_bytes( ottd.PacketAdminType.ADMIN_PACKET_ADMIN_POLL, 1, separator=b'')
		data += util.int_to_bytes( self.update_type, 1, separator=b'')
		data += util.int_to_bytes( self.extra_data, 4, separator=b'')

		length = util.int_to_bytes( len(data) + 2, 2, separator=b'')
		return length + data
	

#----------------------------------------------
#		ADMIN_PACKET_ADMIN_RCON
#----------------------------------------------
class PacketAdminRCON:
	def __init__(self, rcon_cmd: str):
		self.rcon_cmd = rcon_cmd
	
	def to_bytes(self):
		data  = util.int_to_bytes( ottd.PacketAdminType.ADMIN_PACKET_ADMIN_RCON, 1, separator=b'')
		data += util.str_to_bytes( self.rcon_cmd )

		length = util.int_to_bytes( len(data) + 2, 2, separator=b'')
		return length + data



#----------------------------------------------
#		ADMIN_PACKET_ADMIN_GAMESCRIPT
#----------------------------------------------
class PacketAdminGameScript:
	def __init__(self, game_script: str ):
		self.game_script = game_script
	
	def to_bytes(self):
		data  = util.int_to_bytes( ottd.PacketAdminType.ADMIN_PACKET_ADMIN_GAMESCRIPT, 1, separator=b'')
		data += util.str_to_bytes( self.game_script )

		length = util.int_to_bytes( len(data) + 2, 2, separator=b'')
		return length + data



#----------------------------------------------
#		DUMMY_PACKET
#----------------------------------------------

class PacketUpdateFrequency:

	def __init__(self, update_type, frequency) -> None:
		self.update_type = update_type
		self.frequency = frequency
	
	def to_bytes(self):
		data  = util.int_to_bytes( ottd.PacketAdminType.ADMIN_PACKET_ADMIN_UPDATE_FREQUENCY, 1, separator=b'')
		data += util.int_to_bytes( self.update_type, 2, separator=b'')
		data += util.int_to_bytes( self.frequency, 2, separator=b'')

		length = util.int_to_bytes( len(data) + 2, 2, separator=b'')
		return length + data



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

		data = util.int_to_bytes(_chat_type_, 1, separator=b'')
		data += util.int_to_bytes(_dest_type_, 1, separator=b'')
		data += util.int_to_bytes(self.to_id, 4, separator=b'')
		data += util.str_to_bytes(self.message)

		return data
	
	def __external_chat__(self):
		data = util.str_to_bytes(self.app)				# source
		data += util.int_to_bytes(self.color, 2, separator=b'')	# color
		data += util.str_to_bytes(self.app_user)						# user
		data += util.str_to_bytes(self.message)

		return data

	def to_bytes(self) -> bytearray:
		data = b''

		if self.chat_type == ottd.CHAT_TYPE.EXTERNAL:
			data += util.int_to_bytes(ottd.PacketAdminType.ADMIN_PACKET_ADMIN_EXTERNAL_CHAT, 1, separator=b'')
			data += self.__external_chat__()
		else:
			data += util.int_to_bytes(ottd.PacketAdminType.ADMIN_PACKET_ADMIN_CHAT, 1, separator=b'')
			data += self.__chat__()
		
		length = util.int_to_bytes( len(data) + 2, 2, separator=b'')

		return length + data

