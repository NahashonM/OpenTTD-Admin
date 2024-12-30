
import logging
import ctypes
import openttd.ottd_enum as ottdenum
from openttd.ottd_packet_base import BasePacket


log = logging.getLogger("OTTDReceivePacketFactory")



#----------------------------------------------
#		ADMIN_PACKET_SERVER_CLIENT_JOIN
#----------------------------------------------
def client_join_factory(raw_data: bytearray):
	class ClientJoin( BasePacket ):
		_fields_ = [ ("id", ctypes.c_uint32) ]
	
	try: return ClientJoin.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse client_join_packet. Error {e}")
		return None


#----------------------------------------------
#		ADMIN_PACKET_SERVER_CLIENT_INFO
#----------------------------------------------
def client_info_factory(raw_data: bytearray):
	offset = ctypes.sizeof(BasePacket) + 4
	sz_ip = raw_data.index(b'\x00', offset) - offset + 1

	offset += sz_ip
	sz_name = raw_data.index(b'\x00', offset) - offset + 1

	class ClientInfo( BasePacket ):
		_fields_ = [
			("id", ctypes.c_uint32 ),			# sizeof = 4
			("ip", ctypes.c_char * sz_ip ),		#
			("name", ctypes.c_char * sz_name ), #
			("language", ctypes.c_uint8 ),
			("join_date", ctypes.c_uint32 ),
			("company", ctypes.c_uint8 ),
		]
	
	try: return ClientInfo.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse client_info_packet. Error {e}")
		return None
	

#----------------------------------------------
#		ADMIN_PACKET_SERVER_CLIENT_UPDATE
#----------------------------------------------
def client_update_factory(raw_data: bytearray):

	offset = ctypes.sizeof(BasePacket) + 4
	sz_name = raw_data.index(b'\x00', offset) - offset + 1

	class ClientUpdate( BasePacket ):
		_fields_ = [ 
			("id", ctypes.c_uint32),
			("name", ctypes.c_char * sz_name),
			("playas", ctypes.c_uint8),		# team joined
		]
	
	try: return ClientUpdate.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse client_update_packet. Error {e}")
		return None

#----------------------------------------------
#		ADMIN_PACKET_SERVER_CLIENT_QUIT
#----------------------------------------------
def client_quit_factory(raw_data: bytearray):

	class ClientQuit( BasePacket ):
		_fields_ = [ ("id", ctypes.c_uint32) ]
	
	try: return ClientQuit.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse client_quit_packet. Error {e}")
		return None

#----------------------------------------------
#		ADMIN_PACKET_SERVER_CLIENT_ERROR
#----------------------------------------------
def client_error_factory(raw_data: bytearray):

	class ClientError( BasePacket ):
		_fields_ = [ 
			("id", ctypes.c_uint32),
			("error", ctypes.c_uint8),
		]
	
	try: return ClientError.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse client_error_packet. Error {e}")
		return None

#----------------------------------------------
#		ADMIN_PACKET_SERVER_COMPANY_NEW
#----------------------------------------------
def company_new_factory(raw_data: bytearray):

	class CompanyNew( BasePacket ):
		_fields_ = [	("id", ctypes.c_uint8)	]
	
	try: return CompanyNew.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse company_new_packet. Error {e}")
		return None


#----------------------------------------------
#		ADMIN_PACKET_SERVER_COMPANY_INFO
#----------------------------------------------
def company_info_factory(raw_data: bytearray):
	offset = ctypes.sizeof(BasePacket) + 1
	sz_name = raw_data.index(b'\x00', offset) - offset + 1

	offset += sz_name
	sz_president = raw_data.index(b'\x00', offset) - offset + 1

	class CompanyInfo( BasePacket ):
		_fields_ = [
			("id", ctypes.c_uint8 ),
			("name", ctypes.c_char * sz_name ),
			("president", ctypes.c_char * sz_president ),
			("color", ctypes.c_uint8 ),
			("is_protected", ctypes.c_bool ),
			("start_date", ctypes.c_uint32 ),
			("is_ai", ctypes.c_bool ),
			("quaters_bankrupt", ctypes.c_uint8 ),
			# ("share_owners", ctypes.c_uint8 ),
			# ("share_owners", ctypes.c_uint8 * ottdenum.MAX_COMPANY_SHARE_OWNERS ),
		]
	
	try: return CompanyInfo.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse company_info_packet. Error {e}")
		return None


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

	class CompanyEconomy( BasePacket ):
		_fields_ = [
			("id", ctypes.c_uint8 ),
			("money", ctypes.c_int64 ),
			("loan", ctypes.c_int64 ),
			("income", ctypes.c_int64 ),
			("delivered_cargo", ctypes.c_uint16 ),
			("quaters", EconomyQuaters * ottdenum.ECONOMY_INFO_QUARTERS),
		]
	
	try: return CompanyEconomy.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse company_economy_packet. Error {e}")
		return None


#----------------------------------------------
#		ADMIN_PACKET_SERVER_COMPANY_STATS
#----------------------------------------------
def company_stats_factory(raw_data: bytearray):
	print(raw_data)
	class CompanyStats( BasePacket ):
		_fields_ = [
			("id", ctypes.c_uint8 ),
			("vehicles", ctypes.c_uint16 * ottdenum.NetworkVehicleType.NETWORK_VEH_END),
			("stations", ctypes.c_uint16 * ottdenum.NetworkVehicleType.NETWORK_VEH_END),
		]
	
	try: return CompanyStats.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse company_stats_packet. Error {e}")
		return None

#----------------------------------------------
#		ADMIN_PACKET_SERVER_COMPANY_UPDATE
# Whenever a company's details changes
#----------------------------------------------
def company_update_factory(raw_data: bytearray):

	offset = ctypes.sizeof(BasePacket) + 1
	sz_name = raw_data.index(b'\x00', offset) - offset + 1

	offset += sz_name
	sz_president = raw_data.index(b'\x00', offset) - offset + 1

	class CompanyUpdate( BasePacket ):
		_fields_ = [
			("id", ctypes.c_uint8 ),
			("name", ctypes.c_char * sz_name ),
			("president", ctypes.c_char * sz_president ),
			("color", ctypes.c_uint8 ),
			("is_protected", ctypes.c_bool ),
			("quaters_bankrupt", ctypes.c_uint8 ),
			# ("share_owners", ctypes.c_uint8 * ottdenum.MAX_COMPANY_SHARE_OWNERS ),
		]
	
	try: return CompanyUpdate.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse company_update_packet. Error {e}")
		return None


#----------------------------------------------
#		ADMIN_PACKET_SERVER_COMPANY_REMOVE
#----------------------------------------------
def company_remove_factory(raw_data: bytearray):

	class CompanyRemove( BasePacket ):
		_fields_ = [
			("id", ctypes.c_uint8),
			("reason", ctypes.c_uint8),
		]

	try: return CompanyRemove.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse company_remove_packet. Error {e}")
		return None


#----------------------------------------------
#		ADMIN_PACKET_SERVER_PROTOCOL
#----------------------------------------------
def server_protocol_factory(raw_data: bytearray):
	class ServerProtocol( BasePacket ):
		_fields_ = []
	
	try: return ServerProtocol.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse server_protocol_packet. Error {e}")
		return None

#----------------------------------------------
#		ADMIN_PACKET_SERVER_WELCOME
#----------------------------------------------
def server_welcome_factory(raw_data: bytearray):
	offset = ctypes.sizeof(BasePacket)

	sz_name = raw_data.index(b'\x00', offset) - offset + 1
	offset += sz_name

	sz_version = raw_data.index(b'\x00', offset) - offset + 1
	offset += sz_version + ctypes.sizeof(ctypes.c_bool)

	sz_map_name = raw_data.index(b'\x00', offset ) - offset + 1

	class ServerWelcome( BasePacket ):
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
	
	try: return ServerWelcome.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse server_welcome_packet. Error {e}")
		return None
	
#----------------------------------------------
#		ADMIN_PACKET_SERVER_DATE
#----------------------------------------------
def server_date_factory(raw_data: bytearray):

	class ServerDate( BasePacket ):
		_fields_ = [ ('ticks', ctypes.c_uint32 ) ]

	try: return ServerDate.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse server_date_packet. Error {e}")
		return None
	
#----------------------------------------------
#		ADMIN_PACKET_ADMIN_PONG	
#----------------------------------------------
def server_pong_factory(raw_data: bytearray):
	class ServerPong( BasePacket ):
		_fields_ = []

	try: return ServerPong.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse server_pong_packet. Error {e}")
		return None
	
#----------------------------------------------
#		ADMIN_PACKET_SERVER_RCON
#----------------------------------------------
def rcon_results_factory(raw_data: bytearray):

	offset = ctypes.sizeof(BasePacket) + 3
	sz_text = raw_data.index(b'\x00', offset) - offset + 1

	class RCONResult( BasePacket ):
		_fields_ = [
			("console_color", ctypes.c_uint16 ),
			("text", ctypes.c_char * sz_text )
		]
	
	try: return RCONResult.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse rcon_result_packet. Error {e}")
		return None
	
#----------------------------------------------
#		ADMIN_PACKET_SERVER_RCON
#----------------------------------------------
def rcon_end_factory(raw_data: bytearray):

	sz_cmd = len(raw_data) - ctypes.sizeof(BasePacket)

	class RCONEnd( BasePacket ):
		_fields_ = [ ("cmd", ctypes.c_char * sz_cmd ) ]
	
	try: return RCONEnd.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse rcon_end_packet. Error {e}")
		return None
	
#----------------------------------------------
#		ADMIN_PACKET_SERVER_NEWGAME
#----------------------------------------------
def server_new_game_factory(raw_data: bytearray):

	class ServerNewGame( BasePacket ):
		_fields_ = []
	
	try: return ServerNewGame.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse server_newgame_packet. Error {e}")
		return None
	
#----------------------------------------------
#		ADMIN_PACKET_SERVER_SHUTDOWN
#----------------------------------------------
def server_shutdown_factory(raw_data: bytearray):

	class ServerShutdown( BasePacket ):
		_fields_ = []
	
	try: return ServerShutdown.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse server_shutdown_packet. Error {e}")
		return None
	
#----------------------------------------------
#		ADMIN_PACKET_ADMIN_CHAT
#----------------------------------------------
def incoming_chat_packet_factory( raw_data: bytearray ):

	offset = ctypes.sizeof(BasePacket) + 6
	sz_message = raw_data.index(b'\x00', offset) - offset + 1

	class PacketAdminChat(BasePacket):
		_fields_ = [
			('chat_type', ctypes.c_uint8 ),
			('dest_type', ctypes.c_uint8 ),
			('to', ctypes.c_int32 ),
			('message', ctypes.c_char * sz_message )
		]
	
	try: return PacketAdminChat.from_buffer(raw_data)
	except Exception as e: 
		log.error(f"Failed to parse admin_chat_packet. Error {e}")
		return None

#----------------------------------------------
#		ADMIN_PACKET_EXTERNAL_CHAT
#----------------------------------------------
def incoming_external_chat_packet_factory( app: str, app_user: str, message: str, color: int = ottdenum.TextColor.TC_WHITE):
	class PacketAdminChat(BasePacket):
		_fields_ = [
			('app', ctypes.c_char * (len(app) +1) ),
			('color', ctypes.c_uint16 ),
			('app_user', ctypes.c_char * (len(app_user) +1) ),
			('message', ctypes.c_char * (len(message) +1) )
		]
	
	color = max(ottdenum.TextColor.TC_BLUE, min(color, ottdenum.TextColor.TC_BLACK))

	try: 
		return PacketAdminChat( ctypes.sizeof(PacketAdminChat), ottdenum.PacketAdminType.ADMIN_PACKET_ADMIN_EXTERNAL_CHAT, 
					app.encode(), color, app_user.encode(), message.encode() )
	except Exception as e: 
		log.error(f"Failed to parse external_admin_chat_packet. Error {e}")
		return None
	

