
import openttd.openttdtypes as ottd
import openttd.entities as entities
import openttd.packets as pkts
import openttd.util as util
from openttd.tcpsocket import TCPSocket

class OpenTTD:
	def __init__(self, server_ip, server_admin_port, admin_name, admin_password) -> None:
		self.admin_name = admin_name
		self.admin_password = admin_password

		self.server_ip = server_ip
		self.server_port = server_admin_port
	
	def __connect__(self, reconnect = False):
		if reconnect:
			return self.sock.reconnect()

		self.sock = TCPSocket( self.server_ip, self.server_port)
		return self.sock.connect()

	def __network_receive__(self, receive_type, *, release_lock = True ) -> bytearray:
		data = b''

		while True:
			tmp = self.sock.peek(3)

			if len(tmp) != 3: 
				break

			if  util.get_type_from_packet(tmp) != receive_type:
				break
			
			data_length = util.get_length_from_packet(tmp)
			
			data += self.sock.receive_data(data_length, False)
		
		self.sock.receive_data(0, release_lock)
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
	


	def join(self):
		self.__connect__()

		join_pkt = pkts.PacketAdminJoin(self.admin_name, self.admin_password, ottd.ADMIN_CLIENT_VERSION)
		self.sock.send_data(join_pkt.to_bytes())

		data = self.__network_receive__(ottd.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL, release_lock=False)
		protocol_pkt = pkts.PacketServerProtocol( data)

		data = self.__network_receive__(ottd.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME)
		welcome_pkt = pkts.PacketServerWelcome( data )


		print( "----------------------------------")
		print( f"Connected to server {welcome_pkt.server_name} ")
		print( f"version: {welcome_pkt.server_version}, map: {welcome_pkt.map_size}")
		print( f"starting year: {welcome_pkt.start_year}")
		print( f"is_dedicated: {welcome_pkt.is_dedicated}")
		print( "----------------------------------\n")
	
	def disconnect(self):
		pass

	def ping_server(self):
		ping_pkt = pkts.PacketAdminPing()
		self.sock.send_data( ping_pkt.to_bytes() )

		res = self.__network_receive__( ottd.PacketAdminType.ADMIN_PACKET_SERVER_PONG)
		if len(res) > 3:
			return True
		
		return False

	def poll_current_date(self):
		data = self.__poll_info__(  ottd.AdminUpdateType.ADMIN_UPDATE_DATE, 
									ottd.PacketAdminType.ADMIN_PACKET_SERVER_DATE)

		data = util.bytes_to_int(data[3:])

		return util.ConvertDateToYMD(data)
	
	def poll_client_info(self, client_id=0xFFFFFFFF):
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, 
								  ottd.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO, 
								  extra_info=client_id)

		if len(data) == 0: 
			return list()

		return self.__parse_info_from_bytes__(data[3:], entities.Client)
	
	def poll_company_info(self, company_id=0xFFFFFFFF):
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, 
								  ottd.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_INFO, 
								  extra_info=company_id)

		if len(data) == 0: 
			return list()

		return self.__parse_info_from_bytes__(data[3:], entities.Company)
	
	def poll_company_economy(self, company_id=0xFFFFFFFF):
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY, 
								  ottd.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_ECONOMY, 
								  extra_info=company_id)

		if len(data) == 0: 
			return list()

		return self.__parse_info_from_bytes__(data[3:], entities.CompanyEconomy)
		
	def poll_company_stats(self, company_id=0xFFFFFFFF):
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
	


	def run_rcon_cmd(self, rcon_cmd):

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




	
