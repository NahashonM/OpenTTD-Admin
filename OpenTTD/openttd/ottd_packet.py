
import openttd.ottd_util as util
import openttd.ottd_enum as ottdenum

from openttd.ottd_packet_send import *
from openttd.ottd_packet_receive import *


PACKET_FACTORY_MATCH = {
        
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_JOIN		: client_join_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO		: client_info_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_UPDATE		: client_update_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_QUIT		: client_quit_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_ERROR		: client_error_factory ,

	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_NEW		: company_new_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_INFO		: company_info_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_ECONOMY	: company_economy_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_STATS 		: company_stats_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_UPDATE		: company_update_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_REMOVE		: company_remove_factory ,

	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL			: server_protocol_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME			: server_welcome_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_DATE 				: server_date_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_PONG 				: server_pong_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_RCON 				: rcon_results_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_RCON_END			: rcon_end_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_NEWGAME			: server_new_game_factory ,
	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_SHUTDOWN			: server_shutdown_factory ,

	ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_CHAT				: incoming_chat_packet_factory ,
}



def get_packet_length(packet : bytearray):
	return util.bytes_to_int(packet[:2])


def get_packet_type(packet : bytearray):
	return ottdenum.PacketAdminType( packet[2] )
