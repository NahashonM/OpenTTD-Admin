
import ctypes

import openttd.ottd_enum as ottdenum

from openttd.ottd_packet_base import BaseFactory

#----------------------------------------------
#		ADMIN_PACKET_ADMIN_JOIN
#----------------------------------------------

def join_packet_factory(name : str , password : str, version : str):
	class PacketAdminJoin(BaseFactory):
		_fields_ = [
			('password', ctypes.c_char * (len(password) + 1)),
			('name', ctypes.c_char * (len(name) + 1)),
			('version', ctypes.c_char * (len(version) + 1))
		]

	return PacketAdminJoin( ctypes.sizeof(PacketAdminJoin), ottdenum.PacketAdminType.ADMIN_PACKET_ADMIN_JOIN, 
		       				password.encode(), name.encode(), version.encode())

#----------------------------------------------
#		ADMIN_PACKET_ADMIN_PING	
#----------------------------------------------

def ping_packet_factory():
	class PacketAdminPing(BaseFactory):
		_fields_ = [	('__', ctypes.c_uint32)	]

	return PacketAdminPing( ctypes.sizeof(PacketAdminPing), ottdenum.PacketAdminType.ADMIN_PACKET_ADMIN_PING, 0)


#----------------------------------------------
#		ADMIN_PACKET_ADMIN_QUIT	
#----------------------------------------------

def quit_packet_factory():
	class PacketAdminQuit(BaseFactory):
		_fields_ = []

	return PacketAdminQuit( ctypes.sizeof(PacketAdminQuit), ottdenum.PacketAdminType.ADMIN_PACKET_ADMIN_QUIT)


#----------------------------------------------
#		ADMIN_PACKET_ADMIN_POLL
#----------------------------------------------

def poll_packet_factory( poll_type: ottdenum.AdminUpdateType, *, extra_data:int = ottdenum.MAX_UINT):
	class PacketAdminPoll(BaseFactory):
		_fields_ = [
			('poll_type', ctypes.c_uint8),
			('extra_data', ctypes.c_uint32)
		]

	return PacketAdminPoll( ctypes.sizeof(PacketAdminPoll), ottdenum.PacketAdminType.ADMIN_PACKET_ADMIN_POLL, poll_type, extra_data)
	

#----------------------------------------------
#		ADMIN_PACKET_ADMIN_RCON
#----------------------------------------------

def rcon_packet_factory( rcon_cmd: str ):
	class PacketAdminRCON(BaseFactory):
		_fields_ = [
			('cmd', ctypes.c_char * (len(rcon_cmd) +1) )
		]

	return PacketAdminRCON( ctypes.sizeof(PacketAdminRCON), ottdenum.PacketAdminType.ADMIN_PACKET_ADMIN_RCON, rcon_cmd.encode())

#----------------------------------------------
#		ADMIN_PACKET_ADMIN_GAMESCRIPT
#----------------------------------------------

def gamescript_packet_factory( gamescript: str ):
	class PacketAdminGameScript(BaseFactory):
		_fields_ = [
			('script', ctypes.c_char * (len(gamescript) +1) )
		]

	return PacketAdminGameScript( ctypes.sizeof(PacketAdminGameScript), ottdenum.PacketAdminType.ADMIN_PACKET_ADMIN_GAMESCRIPT, gamescript)

#----------------------------------------------
#		ADMIN_PACKET_ADMIN_CHAT
#----------------------------------------------
def chat_packet_factory( chat_type, message: str, * , to: int = 0 ):
	class PacketAdminChat(BaseFactory):
		_fields_ = [
			('chat_type', ctypes.c_uint8 ),
			('dest_type', ctypes.c_uint8 ),
			('to', ctypes.c_int32 ),
			('message', ctypes.c_char * (len(message) +1) )
		]

	return PacketAdminChat( ctypes.sizeof(PacketAdminChat), ottdenum.PacketAdminType.ADMIN_PACKET_ADMIN_CHAT, 
					ottdenum.CHAT_MAP[chat_type][0], ottdenum.CHAT_MAP[chat_type][1], to, message.encode())

#----------------------------------------------
#		ADMIN_PACKET_EXTERNAL_CHAT
#----------------------------------------------

def external_chat_packet_factory( app: str, app_user: str, message: str, color: int = ottdenum.TextColor.TC_WHITE):
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

#----------------------------------------------
#		ADMIN_PACKET_ADMIN_UPDATE_FREQUENCY
#----------------------------------------------

def update_frequency_packet_factory( update_type, frequency):
	class PacketUpdateFrequency(BaseFactory):
		_fields_ = [
			('update_type', ctypes.c_uint16 ),
			('frequency', ctypes.c_uint16 )
		]

	return PacketUpdateFrequency( ctypes.sizeof(PacketUpdateFrequency), ottdenum.PacketAdminType.ADMIN_PACKET_ADMIN_UPDATE_FREQUENCY, update_type, frequency)
