
import openttd.openttdtypes as ottd
import openttd.entities as entities
import openttd.packets as pkts
import openttd.util as util
from openttd.tcpsocket import TCPSocket

import time

class OpenTTD:
	def __init__(self, server_ip, server_admin_port, admin_name, admin_password) -> None:
		self.admin_name = admin_name
		self.admin_password = admin_password

		self.server_ip = server_ip
		self.server_port = server_admin_port
	
	def __connect__(self, reconnect = False) -> bool:
		if reconnect:
			self.sock.reconnect()
			self.update_sock.reconnect()

		self.sock = TCPSocket( self.server_ip, self.server_port)
		self.update_sock = TCPSocket( self.server_ip, self.server_port)
		
		self.sock.connect()
		self.update_sock.connect()

	def __network_receive__(self, receive_type, *, release_lock = True, update_sock = False ) -> bytearray:

		sock = self.sock
		if update_sock :
			sock = self.update_sock

		data = b''

		while True:
			tmp = sock.peek(3)

			if len(tmp) != 3: 
				break

			if  util.get_type_from_packet(tmp) != receive_type:
				break
			
			data_length = util.get_length_from_packet(tmp)
			
			data += sock.receive_data(data_length, False)
		
		sock.receive_data(0, release_lock)
		return data
	
	def __poll_info__(self, send_type, receive_type, extra_info = 0):

		poll_pkt = pkts.PacketAdminPoll(send_type, extra_data=extra_info)
		self.sock.send_data( poll_pkt.to_bytes() )

		return self.__network_receive__(receive_type, release_lock=True)

	def __parse_info_from_bytes__(self, raw_data, info_class):
		i = 0
		info_list = list()
		while i < len(raw_data):
			infor_inst = info_class()
			i += infor_inst.parse_from_bytearray(raw_data[i:])

			info_list.append(infor_inst)
		
		return info_list
	
	def __register_updates__(self, update_type, frequency) -> bool:

		if self.update_sock.is_locked():
			self.update_sock.receive_data(0,release_lock=True)

		update_pkt = pkts.PacketUpdateFrequency( update_type, frequency )
		
		self.update_sock.send_data(update_pkt.to_bytes())

		return True



	def join(self)  -> bool:
		self.__connect__()

		join_pkt = pkts.PacketAdminJoin(self.admin_name, self.admin_password, ottd.ADMIN_CLIENT_VERSION)
		self.sock.send_data(join_pkt.to_bytes())
		self.update_sock.send_data(join_pkt.to_bytes())

		data = self.__network_receive__(ottd.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL, release_lock=False)
		protocol_pkt = pkts.PacketServerProtocol( data)

		_ = self.__network_receive__(ottd.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL, release_lock=False, update_sock=True)

		data = self.__network_receive__(ottd.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME)
		welcome_pkt = pkts.PacketServerWelcome( data )

		_ = self.__network_receive__(ottd.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME, update_sock=True)

		print( "----------------------------------")
		print( f"Connected to server {welcome_pkt.server_name} ")
		print( f"version: {welcome_pkt.server_version}, map: {welcome_pkt.map_size}")
		print( f"starting year: {welcome_pkt.start_year}")
		print( f"game_type: {welcome_pkt.is_dedicated}")
		print( "----------------------------------\n")

		return True
	
	def leave(self) -> bool:
		quit_pkt = pkts.PacketAdminQuit()
		self.sock.send_data(quit_pkt.to_bytes())

		self.update_sock.receive_data(0,release_lock=True)
		self.update_sock.send_data(quit_pkt.to_bytes())

		self.sock.disconnect()
		self.update_sock.disconnect()
		return True



	def ping_server(self) -> bool:
		ping_pkt = pkts.PacketAdminPing()
		self.sock.send_data( ping_pkt.to_bytes() )

		res = self.__network_receive__( ottd.PacketAdminType.ADMIN_PACKET_SERVER_PONG)
		if len(res) > 3:
			return True
		
		return False

	def poll_current_date(self) -> tuple:
		data = self.__poll_info__(  ottd.AdminUpdateType.ADMIN_UPDATE_DATE, 
									ottd.PacketAdminType.ADMIN_PACKET_SERVER_DATE)

		data = util.bytes_to_int(data[3:])

		return util.ConvertDateToYMD(data)
	
	def poll_client_info(self, client_id=0xFFFFFFFF) -> list:
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, 
								  ottd.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO, 
								  extra_info=client_id)

		if len(data) == 0: 
			return list()

		return self.__parse_info_from_bytes__(data[3:], entities.Client)
	
	def poll_company_info(self, company_id=0xFFFFFFFF) -> list:
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, 
								  ottd.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_INFO, 
								  extra_info=company_id)

		if len(data) == 0: 
			return list()

		return self.__parse_info_from_bytes__(data[3:], entities.Company)
	
	def poll_company_economy(self, company_id=0xFFFFFFFF) -> list:
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY, 
								  ottd.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_ECONOMY, 
								  extra_info=company_id)

		if len(data) == 0: 
			return list()

		return self.__parse_info_from_bytes__(data[3:], entities.CompanyEconomy)
		
	def poll_company_stats(self, company_id=0xFFFFFFFF) -> list:
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS, 
								  ottd.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_STATS, 
								  extra_info=company_id)

		if len(data) == 0: 
			return list()

		return self.__parse_info_from_bytes__(data[3:], entities.CompanyStats)



	def chat_all(self, message):
		msg = pkts.PacketAdminChat(ottd.CHAT_TYPE.ALL, message)
		self.sock.send_data(msg.to_bytes())
		self.sock.receive_data(0)
	
	def chat_team(self, company_id, message):
		msg = pkts.PacketAdminChat(ottd.CHAT_TYPE.COMPANY, message, to_id=company_id)
		self.sock.send_data(msg.to_bytes())
		self.sock.receive_data(0)
	
	def chat_client(self, client_id, message):
		msg = pkts.PacketAdminChat(ottd.CHAT_TYPE.CLIENT, message, to_id=client_id)
		self.sock.send_data(msg.to_bytes())
		self.sock.receive_data(0)

	def chat_external(self, source, user, message, color = 0):
		msg = pkts.PacketAdminChat(ottd.CHAT_TYPE.EXTERNAL, message, to_id=3, app=source, app_user=user, color=color)
		self.sock.send_data(msg.to_bytes())
		self.sock.receive_data(0)
	


	def run_rcon_cmd(self, rcon_cmd) -> str:

		cmd = pkts.PacketAdminRCON(rcon_cmd)
		self.sock.send_data(cmd.to_bytes())

		cmd_out = self.__network_receive__(ottd.PacketAdminType.ADMIN_PACKET_SERVER_RCON, release_lock=False)
		end = self.__network_receive__(ottd.PacketAdminType.ADMIN_PACKET_SERVER_RCON_END)

		res = ''
		i = 0
		while i < len(cmd_out):
			i += 3
			v,l = util.get_int_from_bytes( cmd_out[i:], 2) ; i+=l
			s,l = util.get_str_from_bytes( cmd_out[i:]) ; i+=l
			res += s + '\n'
		
		return res
	

	
	def register_date_updates(self, frequency = ottd.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY) -> bool:
		frequency = max(0, min(frequency, ottd.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY))
		return self.__register_updates__( ottd.AdminUpdateType.ADMIN_UPDATE_DATE, frequency)
	
	def register_client_info_updates(self, frequency = ottd.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__register_updates__( ottd.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, frequency)
	
	def register_company_info_updates(self, frequency = ottd.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__register_updates__( ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, frequency)
	
	def register_company_economy_updates(self, frequency = ottd.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY) -> bool:
		return self.__register_updates__( ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY, frequency)
	
	def register_company_stats_updates(self, frequency = ottd.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY ) -> bool:
		return self.__register_updates__( ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS, frequency)
	
	def register_chat_updates(self, frequency = ottd.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__register_updates__( ottd.AdminUpdateType.ADMIN_UPDATE_CHAT, frequency)
	
	def register_console_updates(self, frequency = ottd.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__register_updates__( ottd.AdminUpdateType.ADMIN_UPDATE_CONSOLE, frequency)
	
	# def register_cmd_names_updates(self, frequency = ottd.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
	# 	return self.__register_updates__( ottd.AdminUpdateType.ADMIN_UPDATE_CMD_NAMES, frequency)
	
	def register_cmd_logging_updates(self, frequency = ottd.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__register_updates__( ottd.AdminUpdateType.ADMIN_UPDATE_CMD_LOGGING, frequency)
	
	def register_gamescript_updates(self, frequency = ottd.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__register_updates__( ottd.AdminUpdateType.ADMIN_UPDATE_GAMESCRIPT, frequency)



	# never releases the lock on the update socket
	def get_updates(self) -> list:

		updates = list()
		tmp = self.update_sock.peek()

		while len(tmp):
			_type_ = util.get_type_from_packet( tmp )
			data = self.__network_receive__(_type_, release_lock=False, update_sock=True)

			updates.append(data)
			tmp = self.update_sock.peek()
		
		return updates

	
