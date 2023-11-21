
import time
import logging

import openttd.openttd as ottd
import openttd.ottd_enum as ottdtypes

import entities as entities
import packets as pkts
import openttd as util

from unused.ottdsocket import OTTDSocket

ottdlog = logging.getLogger("OTTDAdmn")


ENTITY_TYPE_MATCH = {
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_DATE 				: entities.ServerDate ,

	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_JOIN		: entities.ClientJoin ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO		: entities.Client ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_UPDATE		: entities.ClientUpdate ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_QUIT		: entities.ClientQuit ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_ERROR		: entities.ClientError ,

	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_NEW		: entities.CompanyNew ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_INFO		: entities.Company ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_UPDATE	: entities.Company ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_REMOVE	: entities.CompanyRemove ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_ECONOMY	: entities.CompanyEconomy ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_STATS 	: entities.CompanyStats ,

	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_RCON 				: entities.RCONResult ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_RCON_END			: entities.RCONEnd ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_PONG 				: entities.ServerPong ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL			: entities.ServerProtocol ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME			: entities.ServerWelcome ,

	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_NEWGAME			: entities.ServerNewGame ,
	ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_SHUTDOWN			: entities.ServerShutdown ,
}


class OpenTTDAdmin:
	def __init__(self, server_ip, admin_port, admin_name, admin_pswd) -> None:
		self.admin_name = admin_name
		self.admin_pswd = admin_pswd

		self.ctrl_sock = OTTDSocket(server_ip, admin_port)
		self.updt_sock = OTTDSocket(server_ip, admin_port)


	def __network_receive__(*, packet_type, packet_class, ottd_socket ) -> object:
		
		pkt_header = ottd_socket.peek(retries=3)
		if len(pkt_header) == 0 or util.get_type_from_packet(pkt_header) != packet_type:
			return None
			
		data_length = util.get_length_from_packet(pkt_header)
		data = ottd_socket.receive_data(data_length)

		_pkt_ = packet_class()
		_pkt_.parse_from_bytearray(data)
		
		return _pkt_
	

	def __network_receive_list__(*,packet_type, packet_class, ottd_socket) -> list:
		pkts = list()
		pkt = OpenTTDAdmin.__network_receive__(packet_type=packet_type, packet_class=packet_class, ottd_socket=ottd_socket)

		while pkt != None:
			pkts.append(pkt)
			pkt = OpenTTDAdmin.__network_receive__(packet_type=packet_type, packet_class=packet_class, ottd_socket=ottd_socket)
		
		return pkts


	def __join_socket__(ottd_socket, admin_name, admin_pswd):
		ottd_socket.disconnect()

		ottd_socket.connect()

		pkt_admin_join = pkts.PacketAdminJoin(admin_name, admin_pswd, ottdtypes.ADMIN_CLIENT_VERSION).to_bytes()
		ottd_socket.send_data( pkt_admin_join )

		pkt_server_protocol = OpenTTDAdmin.__network_receive__(	packet_type=ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL,
																packet_class=entities.ServerProtocol, ottd_socket=ottd_socket )

		if pkt_server_protocol == None:
			ottdlog.error(f"Failed to join server {ottd_socket.ip}:{ottd_socket.port} with user: {admin_name} password: {'*' * len(admin_pswd)}\n--------EXITING--------")
			exit(0)
									
		ottdlog.info(f"Received packet ADMIN_PACKET_SERVER_PROTOCOL from {ottd_socket.ip}:{ottd_socket.port}")

		pkt_welcome = OpenTTDAdmin.__network_receive__(	packet_type=ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME,
														packet_class=entities.ServerWelcome, ottd_socket=ottd_socket )

		if pkt_welcome == None:
			ottdlog.error(f"Failed to join server {ottd_socket.ip}:{ottd_socket.port} with user: {admin_name} password: {'*' * len(admin_pswd)}\n--------EXITING--------")
			exit(0)

		ottdlog.info(f"Received packet ADMIN_PACKET_SERVER_WELCOME from {ottd_socket.ip}:{ottd_socket.port}")
		
		return pkt_server_protocol, pkt_welcome


	def __request_updates__(self, update_type, frequency) -> bool:
		update_pkt = pkts.PacketUpdateFrequency( update_type, frequency ).to_bytes()
		self.updt_sock.send_data(update_pkt)
		return True


	def join_server(self):
		_, pkt_welcome1 = OpenTTDAdmin.__join_socket__(self.ctrl_sock, self.admin_name, self.admin_pswd)
		_, pkt_welcome2 = OpenTTDAdmin.__join_socket__(self.updt_sock, self.admin_name, self.admin_pswd)

		ottdlog.info( "----------------------------------")
		ottdlog.info( f"Connected to server {pkt_welcome2.server_name} ")
		ottdlog.info( f"version: {pkt_welcome2.server_version}, map: {pkt_welcome2.map_size}")
		ottdlog.info( f"starting year: {pkt_welcome2.start_year}")
		ottdlog.info( f"dedicated: {pkt_welcome2.is_dedicated}")
		ottdlog.info( "----------------------------------\n")
	

	def leave_server(self):
		quit_pkt = pkts.PacketAdminQuit().to_bytes()
		self.ctrl_sock.send_data(quit_pkt)
		self.updt_sock.send_data(quit_pkt)

		self.ctrl_sock.disconnect()
		self.updt_sock.disconnect()
	

	def ping_server(self) -> bool:
		ping_pkt = pkts.PacketAdminPing().to_bytes()
		self.ctrl_sock.send_data( ping_pkt )

		res = OpenTTDAdmin.__network_receive__( packet_type=ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_PONG,
												packet_class=entities.ServerPong, ottd_socket=self.ctrl_sock )
		if res:
			return True
		
		return False


	def poll_current_date(self) -> tuple:
		poll_pkt = pkts.PacketAdminPoll( ottdtypes.AdminUpdateType.ADMIN_UPDATE_DATE, extra_data=0).to_bytes()
		self.ctrl_sock.send_data( poll_pkt )

		pkt_date = OpenTTDAdmin.__network_receive__( packet_type=ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_DATE,
													 packet_class=entities.ServerDate, ottd_socket=self.ctrl_sock )

		return pkt_date.YMD
	

	def poll_client_info(self, client_id=ottdtypes.MAX_UINT) -> tuple:
		poll_pkt = pkts.PacketAdminPoll( ottdtypes.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, extra_data=client_id).to_bytes()
		self.ctrl_sock.send_data( poll_pkt )

		clients = OpenTTDAdmin.__network_receive_list__(	packet_type=ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO,
															packet_class=entities.Client, ottd_socket=self.ctrl_sock )

		return clients
	

	def poll_company_info(self, company_id=ottdtypes.MAX_UINT) -> tuple:
		poll_pkt = pkts.PacketAdminPoll( ottdtypes.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, extra_data=company_id).to_bytes()
		self.ctrl_sock.send_data( poll_pkt )

		companies = OpenTTDAdmin.__network_receive_list__(	packet_type=ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_INFO,
															packet_class=entities.Company, ottd_socket=self.ctrl_sock )

		return companies
	

	def poll_company_economy(self, company_id=ottdtypes.MAX_UINT) -> tuple:
		poll_pkt = pkts.PacketAdminPoll( ottdtypes.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY, extra_data=company_id).to_bytes()
		self.ctrl_sock.send_data( poll_pkt )

		economy = OpenTTDAdmin.__network_receive_list__(	packet_type=ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_ECONOMY,
															packet_class=entities.CompanyEconomy, ottd_socket=self.ctrl_sock )

		return economy
	

	def poll_company_stats(self, company_id=ottdtypes.MAX_UINT) -> tuple:
		poll_pkt = pkts.PacketAdminPoll( ottdtypes.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS, extra_data=company_id).to_bytes()
		self.ctrl_sock.send_data( poll_pkt )

		stats = OpenTTDAdmin.__network_receive_list__(	packet_type=ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_STATS,
														packet_class=entities.CompanyStats, ottd_socket=self.ctrl_sock )

		return stats


	def rcon_cmd(self, rcon_cmd) -> str:
		rcmd = pkts.PacketAdminRCON(rcon_cmd).to_bytes()
		self.ctrl_sock.send_data( rcmd )

		cmd_output = OpenTTDAdmin.__network_receive_list__(	packet_type=ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_RCON,
															packet_class=entities.RCONResult, ottd_socket=self.ctrl_sock )

		cmd_end = OpenTTDAdmin.__network_receive__(	packet_type=ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_RCON_END,
													packet_class=entities.RCONEnd, ottd_socket=self.ctrl_sock )
		
		return cmd_output, cmd_end
	

	def chat_all(self, message):
		msg = pkts.PacketAdminChat(ottdtypes.CHAT_TYPE.ALL, message)
		self.ctrl_sock.send_data(msg.to_bytes())
	

	def chat_team(self, company_id, message):
		msg = pkts.PacketAdminChat(ottdtypes.CHAT_TYPE.COMPANY, message, to_id=company_id)
		self.ctrl_sock.send_data(msg.to_bytes())
	

	def chat_client(self, client_id, message):
		msg = pkts.PacketAdminChat(ottdtypes.CHAT_TYPE.CLIENT, message, to_id=client_id)
		self.ctrl_sock.send_data(msg.to_bytes())


	def chat_external(self, source, user, message, color = 0):
		msg = pkts.PacketAdminChat(ottdtypes.CHAT_TYPE.EXTERNAL, message, to_id=3, app=source, app_user=user, color=color)
		self.ctrl_sock.send_data(msg.to_bytes())
	
	# clamp Daily - anually
	def request_date_updates(self, frequency = ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY) -> bool:
		frequency = max(ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY, min(frequency, ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY))
		return self.__request_updates__( ottdtypes.AdminUpdateType.ADMIN_UPDATE_DATE, frequency)
	
	# clamp Daily - automatic
	def request_client_info_updates(self, frequency = ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		frequency = max(ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY, min(frequency, ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC))
		return self.__request_updates__( ottdtypes.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, frequency)
	
	# Only Automatic
	def request_company_info_updates(self) -> bool:
		return self.__request_updates__( ottdtypes.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC)
	
	# clamp weekly - anually
	def request_company_economy_updates(self, frequency = ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY) -> bool:
		frequency = max(ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY, min(frequency, ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY))
		return self.__request_updates__( ottdtypes.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY, frequency)

	# clamp weekly - anually
	def request_company_stats_updates(self, frequency = ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY ) -> bool:
		frequency = max(ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY, min(frequency, ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY))
		return self.__request_updates__( ottdtypes.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS, frequency)
	

	def request_chat_updates(self, frequency = ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__request_updates__( ottdtypes.AdminUpdateType.ADMIN_UPDATE_CHAT, frequency)
	

	def request_console_updates(self, frequency = ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__request_updates__( ottdtypes.AdminUpdateType.ADMIN_UPDATE_CONSOLE, frequency)
	

	def request_cmd_names_updates(self, frequency = ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__request_updates__( ottdtypes.AdminUpdateType.ADMIN_UPDATE_CMD_NAMES, frequency)
	

	def request_cmd_logging_updates(self, frequency = ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__request_updates__( ottdtypes.AdminUpdateType.ADMIN_UPDATE_CMD_LOGGING, frequency)
	

	def request_gamescript_updates(self, frequency = ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__request_updates__( ottdtypes.AdminUpdateType.ADMIN_UPDATE_GAMESCRIPT, frequency)
	

	def get_registered_updates(self):
		updates = list()

		pkt_header = self.updt_sock.peek(retries=3)

		while len(pkt_header):

			pkt_type = util.get_type_from_packet(pkt_header) 
			data = None

				
			if pkt_type == ottdtypes.PacketAdminType.ADMIN_PACKET_SERVER_DATE:
				data = OpenTTDAdmin.__network_receive__(packet_type=pkt_type, packet_class = ENTITY_TYPE_MATCH[pkt_type], ottd_socket = self.updt_sock)
			else:
				data = OpenTTDAdmin.__network_receive_list__(packet_type=pkt_type, packet_class = ENTITY_TYPE_MATCH[pkt_type], ottd_socket = self.updt_sock)
				
			updates.append(data)

			pkt_header = self.updt_sock.peek(retries=3)
		
		return updates



