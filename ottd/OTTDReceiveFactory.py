
import ctypes
import logging
from typing import Optional

from . import OTTDEnums
from .OTTDPacket import OTTDPacket

class OTTDReceiveFactory:
    logger: logging.Logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)


    def __init__(self, *, logger: Optional[logging.Logger] = None):
        if logger is not None:
            self.logger = logger


    def server_protocol(self, raw_data: bytearray):
        class UpdateType(ctypes.Structure):
            _pack_ = 1
            _fields_ = [
               ("is_update", ctypes.c_bool ),
               ("update_type", ctypes.c_uint16 ),
               ("allowed_frequencies", ctypes.c_uint16 ), 
            ]

        class ServerProtocol( OTTDPacket ):
            _fields_ = [
                ("protocol_version", ctypes.c_uint8 ),
                ("update_frequencies", UpdateType * OTTDEnums.AdminUpdateType.ADMIN_UPDATE_END ),
                ("some_bool", ctypes.c_bool ),
            ]
        
        try: 
            return ServerProtocol.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse server_protocol_packet. Error {e}")
            return None
    

    def server_welcome(self, raw_data: bytearray):
        offset = ctypes.sizeof(OTTDPacket)

        sz_name = raw_data.index(b'\x00', offset) - offset + 1
        offset += sz_name

        sz_version = raw_data.index(b'\x00', offset) - offset + 1
        offset += sz_version + ctypes.sizeof(ctypes.c_bool)

        sz_map_name = raw_data.index(b'\x00', offset ) - offset + 1

        class ServerWelcome( OTTDPacket ):
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
            self.logger.error(f"Failed to parse server_welcome_packet. Error {e}")
            return None
    
    
    def server_date(self,raw_data: bytearray):

        class ServerDate(OTTDPacket):
            _fields_ = [ ('ticks', ctypes.c_uint32 ) ]

        try: return ServerDate.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse server_date_packet. Error {e}")
            return None
        

    def server_pong(self,raw_data: bytearray):
        class ServerPong(OTTDPacket):
            _fields_ = []

        try: return ServerPong.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse server_pong_packet. Error {e}")
            return None
        

    def rcon_results(self,raw_data: bytearray):

        offset = ctypes.sizeof(OTTDPacket) + 3
        sz_text = raw_data.index(b'\x00', offset) - offset + 1

        class RCONResult(OTTDPacket):
            _fields_ = [
                ("console_color", ctypes.c_uint16 ),
                ("text", ctypes.c_char * sz_text )
            ]
        
        try: return RCONResult.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse rcon_result_packet. Error {e}")
            return None
        

    def rcon_end(self,raw_data: bytearray):

        sz_cmd = len(raw_data) - ctypes.sizeof(OTTDPacket)

        class RCONEnd(OTTDPacket):
            _fields_ = [ ("cmd", ctypes.c_char * sz_cmd ) ]
        
        try: return RCONEnd.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse rcon_end_packet. Error {e}")
            return None
        

    def server_new_game(self,raw_data: bytearray):

        class ServerNewGame(OTTDPacket):
            _fields_ = []
        
        try: return ServerNewGame.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse server_newgame_packet. Error {e}")
            return None
        

    def server_shutdown(self,raw_data: bytearray):

        class ServerShutdown(OTTDPacket):
            _fields_ = []
        
        try: return ServerShutdown.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse server_shutdown_packet. Error {e}")
            return None
    
    #------------------------------------------------------------------------------

    def client_join(self, raw_data: bytearray):
        class ClientJoin( OTTDPacket ):
            _fields_ = [ ("id", ctypes.c_uint32) ]
        
        try: return ClientJoin.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse client_join_packet. Error {e}")
            return None
    

    def client_info(self, raw_data: bytearray):
        offset = ctypes.sizeof(OTTDPacket) + 4
        sz_ip = raw_data.index(b'\x00', offset) - offset + 1

        offset += sz_ip
        sz_name = raw_data.index(b'\x00', offset) - offset + 1

        class ClientInfo( OTTDPacket ):
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
            self.logger.error(f"Failed to parse client_info_packet. Error {e}")
            return None
    

    def client_update(self, raw_data: bytearray):
        offset = ctypes.sizeof(OTTDPacket) + 4
        sz_name = raw_data.index(b'\x00', offset) - offset + 1

        class ClientUpdate( OTTDPacket ):
            _fields_ = [ 
                ("id", ctypes.c_uint32),
                ("name", ctypes.c_char * sz_name),
                ("company", ctypes.c_uint8),		# team joined
            ]
        
        try: return ClientUpdate.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse client_update_packet. Error {e}")
            return None
    

    def client_quit(self, raw_data: bytearray):
        class ClientQuit( OTTDPacket ):
            _fields_ = [ ("id", ctypes.c_uint32) ]
        
        try: return ClientQuit.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse client_quit_packet. Error {e}")
            return None
    

    def client_error(self, raw_data: bytearray):
        class ClientError( OTTDPacket ):
            _fields_ = [ 
                ("id", ctypes.c_uint32),
                ("error", ctypes.c_uint8),
            ]
        
        try: return ClientError.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse client_error_packet. Error {e}")
            return None
        
    #------------------------------------------------------------------------------

    def company_new(self,raw_data: bytearray):
        class CompanyNew(OTTDPacket):
            _fields_ = [	("id", ctypes.c_uint8)	]
        
        try: return CompanyNew.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse company_new_packet. Error {e}")
            return None


    def company_info(self,raw_data: bytearray):
        offset = ctypes.sizeof(OTTDPacket) + 1
        sz_name = raw_data.index(b'\x00', offset) - offset + 1

        offset += sz_name
        sz_president = raw_data.index(b'\x00', offset) - offset + 1

        class CompanyInfo(OTTDPacket):
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
                # ("share_owners", ctypes.c_uint8 * OTTDEnums.MAX_COMPANY_SHARE_OWNERS ),
            ]
        
        try: return CompanyInfo.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse company_info_packet. Error {e}")
            return None


    def company_economy(self,raw_data: bytearray):
        class EconomyQuaters(OTTDPacket):
            _pack_ = 1
            _fields_ = [
                ("value", ctypes.c_int64),
                ("performance_history", ctypes.c_int16),
                ("delivered_cargo", ctypes.c_uint16),
            ]

        class CompanyEconomy(OTTDPacket):
            _fields_ = [
                ("id", ctypes.c_uint8 ),
                ("money", ctypes.c_int64 ),
                ("loan", ctypes.c_int64 ),
                ("income", ctypes.c_int64 ),
                ("delivered_cargo", ctypes.c_uint16 ),
                ("quaters", EconomyQuaters * OTTDEnums.ECONOMY_INFO_QUARTERS),
            ]
        
        try: return CompanyEconomy.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse company_economy_packet. Error {e}")
            return None


    def company_stats(self,raw_data: bytearray):
        print(raw_data)
        class CompanyStats(OTTDPacket):
            _fields_ = [
                ("id", ctypes.c_uint8 ),
                ("vehicles", ctypes.c_uint16 * OTTDEnums.NetworkVehicleType.NETWORK_VEH_END),
                ("stations", ctypes.c_uint16 * OTTDEnums.NetworkVehicleType.NETWORK_VEH_END),
            ]
        
        try: return CompanyStats.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse company_stats_packet. Error {e}")
            return None


    def company_update(self,raw_data: bytearray):
        offset = ctypes.sizeof(OTTDPacket) + 1
        sz_name = raw_data.index(b'\x00', offset) - offset + 1

        offset += sz_name
        sz_president = raw_data.index(b'\x00', offset) - offset + 1

        class CompanyUpdate(OTTDPacket):
            _fields_ = [
                ("id", ctypes.c_uint8 ),
                ("name", ctypes.c_char * sz_name ),
                ("president", ctypes.c_char * sz_president ),
                ("color", ctypes.c_uint8 ),
                ("is_protected", ctypes.c_bool ),
                ("quaters_bankrupt", ctypes.c_uint8 ),
                # ("share_owners", ctypes.c_uint8 * OTTDEnums.MAX_COMPANY_SHARE_OWNERS ),
            ]
        
        try: return CompanyUpdate.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse company_update_packet. Error {e}")
            return None


    def company_remove(self,raw_data: bytearray):

        class CompanyRemove(OTTDPacket):
            _fields_ = [
                ("id", ctypes.c_uint8),
                ("reason", ctypes.c_uint8),
            ]

        try: return CompanyRemove.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse company_remove_packet. Error {e}")
            return None

    #------------------------------------------------------------------------------

    def chat_packet(self,raw_data: bytearray ):

        offset = ctypes.sizeof(OTTDPacket) + 6
        sz_message = raw_data.index(b'\x00', offset) - offset + 1

        class PacketAdminChat(OTTDPacket):
            _fields_ = [
                ('chat_type', ctypes.c_uint8 ),
                ('dest_type', ctypes.c_uint8 ),
                ('fro', ctypes.c_int32 ),
                ('message', ctypes.c_char * sz_message )
            ]
        
        try: return PacketAdminChat.from_buffer(raw_data)
        except Exception as e: 
            self.logger.error(f"Failed to parse admin_chat_packet. Error {e}")
            return None


    def incoming_external_chat_packet(self,app: str, app_user: str, message: str, color: int = OTTDEnums.TextColor.TC_WHITE):
        class PacketAdminChat(OTTDPacket):
            _fields_ = [
                ('app', ctypes.c_char * (len(app) +1) ),
                ('color', ctypes.c_uint16 ),
                ('app_user', ctypes.c_char * (len(app_user) +1) ),
                ('message', ctypes.c_char * (len(message) +1) )
            ]
        
        color = max(OTTDEnums.TextColor.TC_BLUE, min(color, OTTDEnums.TextColor.TC_BLACK))

        try: 
            return PacketAdminChat( ctypes.sizeof(PacketAdminChat), OTTDEnums.PacketAdminType.ADMIN_PACKET_ADMIN_EXTERNAL_CHAT, 
                        app.encode(), color, app_user.encode(), message.encode() )
        except Exception as e: 
            self.logger.error(f"Failed to parse external_admin_chat_packet. Error {e}")
            return None
        
    #------------------------------------------------------------------------------
    

    PACKET_FACTORY_MATCH = {
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL	: server_protocol,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME	: server_welcome,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_DATE	    : server_date,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_PONG	    : server_pong,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_RCON	    : rcon_results,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_RCON_END	: rcon_end,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_NEWGAME	: server_new_game,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_SHUTDOWN	: server_shutdown,

        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_JOIN	: client_join,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO	: client_info,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_UPDATE	: client_update,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_QUIT	: client_quit,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_ERROR	: client_error,

        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_NEW	    : company_new,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_INFO	    : company_info,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_ECONOMY	: company_economy,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_STATS	    : company_stats,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_UPDATE	: company_update,
        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_REMOVE	: company_remove,

        OTTDEnums.PacketAdminType.ADMIN_PACKET_SERVER_CHAT	: chat_packet,

        
    }



