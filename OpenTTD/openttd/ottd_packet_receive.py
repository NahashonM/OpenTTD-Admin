
import ctypes
import openttd.ottd_enum as ottdenum
from openttd.ottd_packet_base import BasePacket, BaseFactory


#----------------------------------------------
#		ADMIN_PACKET_SERVER_CLIENT_JOIN
#----------------------------------------------
def client_join_factory(raw_data: bytearray):
	class ClientJoin( BaseFactory ):
		_fields_ = [ ("id", ctypes.c_uint32) ]
	
	return ClientJoin.from_buffer(raw_data)


#----------------------------------------------
#		ADMIN_PACKET_SERVER_CLIENT_INFO
#----------------------------------------------
def client_info_factory(raw_data: bytearray):
	offset = ctypes.sizeof(BaseFactory) + 4
	sz_ip = raw_data.index(b'\x00', offset) - offset + 1

	offset += sz_ip
	sz_name = raw_data.index(b'\x00', offset) - offset + 1

	class ClientInfo( BaseFactory ):
		_fields_ = [
			("id", ctypes.c_uint32 ),
			("ip", ctypes.c_char * sz_ip ),
			("name", ctypes.c_char * sz_name ),
			("language", ctypes.c_uint8 ),
			("join_date", ctypes.c_uint32 ),
			("company", ctypes.c_uint8 ),
		]
	
	return ClientInfo.from_buffer(raw_data)

#----------------------------------------------
#		ADMIN_PACKET_SERVER_CLIENT_UPDATE
#----------------------------------------------
def client_update_factory(raw_data: bytearray):

	offset = ctypes.sizeof(BaseFactory) + 4
	sz_name = raw_data.index(b'\x00', offset) - offset + 1

	class ClientUpdate( BaseFactory ):
		_fields_ = [ 
			("id", ctypes.c_uint32),
			("name", ctypes.c_char * sz_name),
			("playas", ctypes.c_uint8),		# team joined
		]
	
	return ClientUpdate.from_buffer(raw_data)

#----------------------------------------------
#		ADMIN_PACKET_SERVER_CLIENT_QUIT
#----------------------------------------------
def client_quit_factory(raw_data: bytearray):

	class ClientQuit( BaseFactory ):
		_fields_ = [ ("id", ctypes.c_uint32) ]
	
	return ClientQuit.from_buffer(raw_data)

#----------------------------------------------
#		ADMIN_PACKET_SERVER_CLIENT_ERROR
#----------------------------------------------
def client_error_factory(raw_data: bytearray):

	class ClientError( BaseFactory ):
		_fields_ = [ 
			("id", ctypes.c_uint32),
			("error", ctypes.c_uint8),
		]
	
	return ClientError.from_buffer(raw_data)

#----------------------------------------------
#		ADMIN_PACKET_SERVER_COMPANY_NEW
#----------------------------------------------
def company_new_factory(raw_data: bytearray):

	class CompanyNew( BaseFactory ):
		_fields_ = [	("id", ctypes.c_uint8)	]
	
	return CompanyNew.from_buffer(raw_data)


#----------------------------------------------
#		ADMIN_PACKET_SERVER_COMPANY_INFO
#----------------------------------------------
def company_info_factory(raw_data: bytearray):
	offset = ctypes.sizeof(BaseFactory) + 1
	sz_name = raw_data.index(b'\x00', offset) - offset + 1

	offset += sz_name
	sz_president = raw_data.index(b'\x00', offset) - offset + 1

	class CompanyInfo( BaseFactory ):
		_fields_ = [
			("id", ctypes.c_uint8 ),
			("name", ctypes.c_char * sz_name ),
			("president", ctypes.c_char * sz_president ),
			("color", ctypes.c_uint8 ),
			("is_protected", ctypes.c_bool ),
			("start_date", ctypes.c_uint32 ),
			("is_ai", ctypes.c_bool ),
			("quaters_bankrupt", ctypes.c_uint8 ),
			("share_owners", ctypes.c_uint8 * ottdenum.MAX_COMPANY_SHARE_OWNERS ),
		]
	
	return CompanyInfo.from_buffer(raw_data)


#----------------------------------------------
#		ADMIN_PACKET_SERVER_COMPANY_ECONOMY
#----------------------------------------------
def company_economy_factory(raw_data: bytearray):
	class EconomyQuaters( BasePacket ):
		_pack_ = 1
		_fields_ = [
			("value", ctypes.c_int64),
			("performance_history", ctypes.c_int16),
			("delivered_cargo", ctypes.c_uint16),
		]

	class CompanyEconomy( BaseFactory ):
		_fields_ = [
			("id", ctypes.c_uint8 ),
			("money", ctypes.c_int64 ),
			("loan", ctypes.c_int64 ),
			("income", ctypes.c_int64 ),
			("delivered_cargo", ctypes.c_uint16 ),
			("quaters", EconomyQuaters * ottdenum.ECONOMY_INFO_QUARTERS),
		]
	
	return CompanyEconomy.from_buffer(raw_data)


#----------------------------------------------
#		ADMIN_PACKET_SERVER_COMPANY_STATS
#----------------------------------------------
def company_stats_factory(raw_data: bytearray):
	print(raw_data)
	class CompanyStats( BaseFactory ):
		_fields_ = [
			("id", ctypes.c_uint8 ),
			("vehicles", ctypes.c_uint16 * ottdenum.NetworkVehicleType.NETWORK_VEH_END),
			("stations", ctypes.c_uint16 * ottdenum.NetworkVehicleType.NETWORK_VEH_END),
		]
	
	return CompanyStats.from_buffer(raw_data)

#----------------------------------------------
#		ADMIN_PACKET_SERVER_COMPANY_UPDATE
# Whenever a company's details changes
#----------------------------------------------
def company_update_factory(raw_data: bytearray):

	offset = ctypes.sizeof(BaseFactory) + 1
	sz_name = raw_data.index(b'\x00', offset) - offset + 1

	offset += sz_name
	sz_president = raw_data.index(b'\x00', offset) - offset + 1

	class CompanyUpdate( BaseFactory ):
		_fields_ = [
			("id", ctypes.c_uint8 ),
			("name", ctypes.c_char * sz_name ),
			("president", ctypes.c_char * sz_president ),
			("color", ctypes.c_uint8 ),
			("is_protected", ctypes.c_bool ),
			("quaters_bankrupt", ctypes.c_uint8 ),
			("share_owners", ctypes.c_uint8 * ottdenum.MAX_COMPANY_SHARE_OWNERS ),
		]
	
	return CompanyUpdate.from_buffer(raw_data)


#----------------------------------------------
#		ADMIN_PACKET_SERVER_COMPANY_REMOVE
#----------------------------------------------
def company_remove_factory(raw_data: bytearray):

	class CompanyRemove( BaseFactory ):
		_fields_ = [
			("id", ctypes.c_uint8),
			("reason", ctypes.c_uint8),
		]
	
	return CompanyRemove.from_buffer(raw_data)


#----------------------------------------------
#		ADMIN_PACKET_SERVER_PROTOCOL
#----------------------------------------------
def server_protocol_factory(raw_data: bytearray):
	class ServerProtocol( BaseFactory ):
		_fields_ = []

	return ServerProtocol.from_buffer(raw_data)

#----------------------------------------------
#		ADMIN_PACKET_SERVER_WELCOME
#----------------------------------------------
def server_welcome_factory(raw_data: bytearray):
	offset = ctypes.sizeof(BaseFactory)

	sz_name = raw_data.index(b'\x00', offset) - offset + 1
	offset += sz_name

	sz_version = raw_data.index(b'\x00', offset) - offset + 1
	offset += sz_version + ctypes.sizeof(ctypes.c_bool)

	sz_map_name = raw_data.index(b'\x00', offset ) - offset + 1

	class ServerWelcome( BaseFactory ):
		_fields_ = [
			("name", ctypes.c_char * sz_name ),
			("version", ctypes.c_char * sz_version ),
			("is_dedicated", ctypes.c_bool ),
			("map_name", ctypes.c_char * sz_map_name ),
			("seed", ctypes.c_uint32 ),
			("landscape", ctypes.c_uint8 ),
			("start_year", ctypes.c_uint32 ),
			("x", ctypes.c_uint16 ),
			("y", ctypes.c_uint16 ),
		]
	
	return ServerWelcome.from_buffer(raw_data)

#----------------------------------------------
#		ADMIN_PACKET_SERVER_DATE
#----------------------------------------------
def server_date_factory(raw_data: bytearray):

	class ServerDate( BaseFactory ):
		_fields_ = [ ('ticks', ctypes.c_uint32 ) ]

	return ServerDate.from_buffer(raw_data)

#----------------------------------------------
#		ADMIN_PACKET_ADMIN_PONG	
#----------------------------------------------
def server_pong_factory(raw_data: bytearray):
	class ServerPong( BaseFactory ):
		_fields_ = []

	return ServerPong.from_buffer(raw_data)


#----------------------------------------------
#		ADMIN_PACKET_SERVER_RCON
#----------------------------------------------
def rcon_results_factory(raw_data: bytearray):

	offset = ctypes.sizeof(BaseFactory) + 3
	sz_text = raw_data.index(b'\x00', offset) - offset + 1

	class RCONResult( BaseFactory ):
		_fields_ = [
			("console_color", ctypes.c_uint16 ),
			("text", ctypes.c_char * sz_text )
		]
	
	return RCONResult.from_buffer(raw_data)


#----------------------------------------------
#		ADMIN_PACKET_SERVER_RCON
#----------------------------------------------
def rcon_end_factory(raw_data: bytearray):

	sz_cmd = len(raw_data) - ctypes.sizeof(BaseFactory)

	class RCONEnd( BaseFactory ):
		_fields_ = [ ("cmd", ctypes.c_char * sz_cmd ) ]
	
	return RCONEnd.from_buffer(raw_data)


#----------------------------------------------
#		ADMIN_PACKET_SERVER_NEWGAME
#----------------------------------------------
def server_new_game_factory(raw_data: bytearray):

	class ServerNewGame( BaseFactory ):
		_fields_ = []
	
	return ServerNewGame.from_buffer(raw_data)


#----------------------------------------------
#		ADMIN_PACKET_SERVER_SHUTDOWN
#----------------------------------------------
def server_shutdown_factory(raw_data: bytearray):

	class ServerShutdown( BaseFactory ):
		_fields_ = []

	return ServerShutdown.from_buffer(raw_data)



#----------------------------------------------
#		ADMIN_PACKET_ADMIN_CHAT
#----------------------------------------------
def incoming_chat_packet_factory( raw_data: bytearray ):

	offset = ctypes.sizeof(BaseFactory) + 6
	sz_message = raw_data.index(b'\x00', offset) - offset + 1

	class PacketAdminChat(BaseFactory):
		_fields_ = [
			('chat_type', ctypes.c_uint8 ),
			('dest_type', ctypes.c_uint8 ),
			('to', ctypes.c_int32 ),
			('message', ctypes.c_char * sz_message )
		]
	
	return PacketAdminChat.from_buffer(raw_data)


#----------------------------------------------
#		ADMIN_PACKET_EXTERNAL_CHAT
#----------------------------------------------

def incoming_external_chat_packet_factory( app: str, app_user: str, message: str, color: int = ottdenum.TextColor.TC_WHITE):
	class PacketAdminChat(BaseFactory):
		_fields_ = [
			('app', ctypes.c_char * (len(app) +1) ),
			('color', ctypes.c_uint16 ),
			('app_user', ctypes.c_char * (len(app_user) +1) ),
			('message', ctypes.c_char * (len(message) +1) )
		]
	
	color = max(ottdenum.TextColor.TC_BLUE, min(color, ottdenum.TextColor.TC_BLACK))

	return PacketAdminChat( ctypes.sizeof(PacketAdminChat), ottdenum.PacketAdminType.ADMIN_PACKET_ADMIN_EXTERNAL_CHAT, 
					app.encode(), color, app_user.encode(), message.encode() )
