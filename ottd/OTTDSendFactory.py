
import ctypes
import logging
from typing import Optional

from . import OTTDEnums
from .OTTDPacket import OTTDPacket

class OTTDSendFactory:
    logger: logging.Logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    
    def __init__(self, *, logger: Optional[logging.Logger] = None):
        if logger is not None:
            self.logger = logger
    

    def join_packet(self, name : str , password : str, version : str):
        class PacketAdminJoin(OTTDPacket):
            _fields_ = [
                ('password', ctypes.c_char * (len(password) + 1)),
                ('name', ctypes.c_char * (len(name) + 1)),
                ('version', ctypes.c_char * (len(version) + 1)),
            ]

        return PacketAdminJoin(ctypes.sizeof(PacketAdminJoin), 
                               OTTDEnums.PacketAdminType.ADMIN_PACKET_ADMIN_JOIN, 
                               password.encode(), name.encode(), version.encode())
    

    def quit_packet(self):
        class PacketAdminQuit(OTTDPacket):
            _fields_ = []

        return PacketAdminQuit( ctypes.sizeof(PacketAdminQuit), OTTDEnums.PacketAdminType.ADMIN_PACKET_ADMIN_QUIT)
    
    
    def ping_packet(self):
        class PacketAdminPing(OTTDPacket):
            _fields_ = [	('__', ctypes.c_uint32)	]

        return PacketAdminPing( ctypes.sizeof(PacketAdminPing), OTTDEnums.PacketAdminType.ADMIN_PACKET_ADMIN_PING, 0)
    
    
    def poll_packet(self, poll_type: OTTDEnums.AdminUpdateType, *, extra_data:int = OTTDEnums.MAX_UINT):
        class PacketAdminPoll(OTTDPacket):
            _fields_ = [
                ('poll_type', ctypes.c_uint8),
                ('extra_data', ctypes.c_uint32)
            ]

        return PacketAdminPoll( ctypes.sizeof(PacketAdminPoll), 
                               OTTDEnums.PacketAdminType.ADMIN_PACKET_ADMIN_POLL, poll_type, extra_data)
    

    def update_packet(self, update_type: OTTDEnums.AdminUpdateType, frequency: OTTDEnums.AdminUpdateFrequency):
        class PacketUpdateFrequency(OTTDPacket):
            _fields_ = [
                ('update_type', ctypes.c_uint16 ),
                ('frequency', ctypes.c_uint16 )
            ]

        return PacketUpdateFrequency( ctypes.sizeof(PacketUpdateFrequency), 
                                     OTTDEnums.PacketAdminType.ADMIN_PACKET_ADMIN_UPDATE_FREQUENCY, update_type, frequency)
    
    def rcon_packet(self, rcon_cmd: str ):
        class PacketAdminRCON(OTTDPacket):
            _fields_ = [
                ('cmd', ctypes.c_char * (len(rcon_cmd) +1) )
            ]

        return PacketAdminRCON( ctypes.sizeof(PacketAdminRCON), OTTDEnums.PacketAdminType.ADMIN_PACKET_ADMIN_RCON, rcon_cmd.encode())


    def gamescript_packet(self, gamescript: str ):
        class PacketAdminGameScript(OTTDPacket):
            _fields_ = [
                ('script', ctypes.c_char * (len(gamescript) +1) )
            ]

        return PacketAdminGameScript( ctypes.sizeof(PacketAdminGameScript), 
                                     OTTDEnums.PacketAdminType.ADMIN_PACKET_ADMIN_GAMESCRIPT, gamescript)
    

    def chat_packet(self, chat_type, message: str, * , to: int = 0 ):
        class PacketAdminChat(OTTDPacket):
            _fields_ = [
                ('chat_type', ctypes.c_uint8 ),
                ('dest_type', ctypes.c_uint8 ),
                ('to', ctypes.c_int32 ),
                ('message', ctypes.c_char * (len(message) +1) )
            ]

        return PacketAdminChat( 
             ctypes.sizeof(PacketAdminChat), 
             OTTDEnums.PacketAdminType.ADMIN_PACKET_ADMIN_CHAT,
             OTTDEnums.CHAT_MAP[chat_type][0], 
             OTTDEnums.CHAT_MAP[chat_type][1], 
             to, message.encode())
    

    def external_chat_packet(self, app: str, app_user: str, message: str, color: int = OTTDEnums.TextColor.TC_WHITE):
        class PacketAdminChat(OTTDPacket):
            _fields_ = [
                ('app', ctypes.c_char * (len(app) +1) ),
                ('color', ctypes.c_uint16 ),
                ('app_user', ctypes.c_char * (len(app_user) +1) ),
                ('message', ctypes.c_char * (len(message) +1) )
            ]
	
        color = max(OTTDEnums.TextColor.TC_BLUE, min(color, OTTDEnums.TextColor.TC_BLACK))

        return PacketAdminChat( 
            ctypes.sizeof(PacketAdminChat), 
            OTTDEnums.PacketAdminType.ADMIN_PACKET_ADMIN_EXTERNAL_CHAT, 
			app.encode(), color, app_user.encode(), message.encode() )



