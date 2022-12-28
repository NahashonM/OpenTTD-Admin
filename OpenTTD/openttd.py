
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
	
	def join(self):
		self.__connect__()

		join_pkt = pkts.PacketAdminJoin(self.admin_name, self.admin_password, ottd.ADMIN_CLIENT_VERSION)
		self.sock.send_data(join_pkt.to_bytes())

		raw_data = self.sock.receive_data()
		protocol_pkt = pkts.PacketServerProtocol( raw_data )

		raw_data = self.sock.receive_data()
		welcome_pkt = pkts.PacketServerWelcome(  raw_data  )

		print( "----------------------------------")
		print( f"Connected to server {welcome_pkt.server_name} ")
		print( f"version: {welcome_pkt.server_version}, map: {welcome_pkt.map_size}")
		print( f"starting year: {welcome_pkt.start_year}")
		print( f"is_dedicated: {welcome_pkt.is_dedicated}")
		print( "----------------------------------\n")
	

	def __poll_info__(self, info_type, extra_info = 0):

		poll_pkt = pkts.PacketAdminPoll(info_type, extra_data=extra_info)
		self.sock.send_data( poll_pkt.to_bytes() )

		large_data = False
		if extra_info == ottd.MAX_UINT:
			large_data = True
		
		return self.sock.receive_data(large_data=large_data)
	
	def __parse_info_from_bytes__(self, raw_data, info_class):
		i = 0
		info_list = list()
		while i < len(raw_data):
			infor_inst = info_class()
			i += infor_inst.parse_from_bytearray(raw_data[i:])

			info_list.append(infor_inst)
		
		return info_list
	


	def poll_current_date(self):
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_DATE)

		if util.get_type_from_packet(data) != ottd.PacketAdminType.ADMIN_PACKET_SERVER_DATE:
			raise RuntimeError( f"Got {util.get_type_from_packet(data).name} when expecting ADMIN_PACKET_SERVER_DATE")
		
		data = util.bytes_to_int(data[3:])

		return util.ConvertDateToYMD(data)
	
	def poll_client_info(self, client_id=0xFFFFFFFF):
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, extra_info=client_id)

		if len(data) == 0: return list()
		
		if util.get_type_from_packet(data) != ottd.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO:
			raise RuntimeError( f"Got {util.get_type_from_packet(data).name} when expecting ADMIN_PACKET_SERVER_CLIENT_INFO")
		
		return self.__parse_info_from_bytes__(data[3:], entities.Client)
	
	def poll_company_info(self, company_id=0xFFFFFFFF):
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, extra_info=company_id)

		if len(data) == 0: return list()

		if util.get_type_from_packet(data) != ottd.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_INFO:
			raise RuntimeError( f"Got {util.get_type_from_packet(data).name} when expecting ADMIN_PACKET_SERVER_COMPANY_INFO")
		
		return self.__parse_info_from_bytes__(data[3:], entities.Company)
	
	def poll_company_economy(self, company_id=0xFFFFFFFF):
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY, extra_info=company_id)

		if len(data) == 0: return list()

		if util.get_type_from_packet(data) != ottd.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_ECONOMY:
			raise RuntimeError( f"Got {util.get_type_from_packet(data).name} when expecting ADMIN_PACKET_SERVER_COMPANY_ECONOMY")
		
		return self.__parse_info_from_bytes__(data[3:], entities.CompanyEconomy)
		
	def poll_company_stats(self, company_id=0xFFFFFFFF):
		data = self.__poll_info__(ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS, extra_info=company_id)

		if len(data) == 0: return list()

		if util.get_type_from_packet(data) != ottd.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_STATS:
			raise RuntimeError( f"Got {util.get_type_from_packet(data).name} when expecting ADMIN_PACKET_SERVER_COMPANY_STATS")
		
		return self.__parse_info_from_bytes__(data[3:], entities.CompanyStats)

	

	def chat_all(self, message):
		msg = pkts.PacketAdminChat(ottd.CHAT_TYPE.ALL, message)
		self.sock.send_data(msg.to_bytes())
	
	def chat_team(self, company_id, message):
		msg = pkts.PacketAdminChat(ottd.CHAT_TYPE.COMPANY, message, to_id=company_id)
		self.sock.send_data(msg.to_bytes())
	
	def chat_client(self, client_id, message):
		msg = pkts.PacketAdminChat(ottd.CHAT_TYPE.CLIENT, message, to_id=client_id)
		self.sock.send_data(msg.to_bytes())

	def chat_external(self, source, user, message, color = 0):
		msg = pkts.PacketAdminChat(ottd.CHAT_TYPE.EXTERNAL, message, to_id=3, app=source, app_user=user, color=color)
		self.sock.send_data(msg.to_bytes())

	def disconnect(self):
		pass
