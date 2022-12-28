
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
	
	

	def poll_info(self, info_type, receive_type: ottd.PacketAdminType, info_id):
		poll_packet = PacketAdminPoll()
		poll_packet.poll(info_type, self.client_sock, extra_data=info_id)

		data = b''
		d = DummyPacket()

		i = 1
		if info_id == 0xFFFFFFFF:
			i = 0

		while i < 2:
			d.receive_data(self.client_sock)
			data += d.get_data() + b'000'
			i += 1
		
		if d.get_type() != receive_type:
			print(d.get_data())
			raise RuntimeError(f"Got {d.get_type()} when expecting {receive_type}")


		return data
	
	def parse_info_from_bytes(self, info_class, bytes_data):
		i = 0
		info_list = list()
		while i < len(bytes_data):
			infor_inst = info_class()
			i += infor_inst.parse_from_bytearray(bytes_data[i:])

			info_list.append(infor_inst)
		
		return info_list


	def poll_current_date(self):
		data = self.poll_info(
			ottd.AdminUpdateType.ADMIN_UPDATE_DATE,
			ottd.PacketAdminType.ADMIN_PACKET_SERVER_DATE,
			0
			)
		data = Packet.bytes_to_int(data[:4])
		return Date.ConvertDateToYMD(data)

	def poll_client_info(self, client_id=0xFFFFFFFF):
		data = self.poll_info(
			ottd.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO,
			ottd.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO,
			client_id
			)

		return self.parse_info_from_bytes(entities.Client, data)
	
	def poll_company_info(self, company_id=0xFFFFFFFF):
		data = self.poll_info(
			ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO,
			ottd.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_INFO,
			company_id
			)

		return self.parse_info_from_bytes(entities.Company, data)

	def poll_company_economy(self, company_id=0xFFFFFFFF):
		data = self.poll_info(
			ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY,
			ottd.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_ECONOMY,
			company_id
			)

		return self.parse_info_from_bytes(entities.CompanyEconomy, data)

	def poll_company_stats(self, company_id=0xFFFFFFFF):
		data = self.poll_info(
			ottd.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS,
			ottd.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_STATS,
			company_id
			)

		return self.parse_info_from_bytes(entities.CompanyStats, data)
	
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
