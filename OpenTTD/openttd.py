

from OpenTTD.network.packet_types import PacketAdminJoin
from OpenTTD.network.packet_types import PacketServerWelcome
from OpenTTD.network.packet_types import PacketAdminChat
from OpenTTD.network.packet_types import PacketServerProtocol
from OpenTTD.network.packet_types import PacketAdminPoll
from OpenTTD.network.packet_types import DummyPacket
from OpenTTD.network.packet import Packet

from OpenTTD.date import Date

import OpenTTD.entities as entities
import OpenTTD.enums as types
import time


import socket

class OpenTTD:
	def __init__(self, server_ip, server_admin_port, admin_name, admin_password) -> None:
		self.server_ip = server_ip
		self.server_admin_port = server_admin_port

		self.admin_name = admin_name
		self.admin_password = admin_password

		self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


	def connect(self):

		self.client_sock.connect((self.server_ip, self.server_admin_port))
		
		join_packet = PacketAdminJoin(self.admin_name, self.admin_password, types.ADMIN_CLIENT_VERSION)
		join_packet.send_data(self.client_sock)

		protocol_packet = PacketServerProtocol()
		protocol_packet.receive_data(self.client_sock)

		welcome_packet = PacketServerWelcome()
		welcome_packet.receive_data( self.client_sock)

		print( "----------------------------------")
		print( f"Connected to server {welcome_packet.server_name} ")
		print( f"version: {welcome_packet.server_version}, map: {welcome_packet.map_size}")
		print( f"starting year: {welcome_packet.start_year}")
		print( "game type: ", welcome_packet.game_type)
		print( "----------------------------------\n")
	

	def poll_info(self, info_type, receive_type: types.PacketAdminType, info_id):
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
			types.AdminUpdateType.ADMIN_UPDATE_DATE,
			types.PacketAdminType.ADMIN_PACKET_SERVER_DATE,
			0
			)
		data = Packet.bytes_to_int(data[:4])
		return Date.ConvertDateToYMD(data)

	def poll_client_info(self, client_id=0xFFFFFFFF):
		data = self.poll_info(
			types.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO,
			types.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO,
			client_id
			)

		return self.parse_info_from_bytes(entities.Client, data)
	
	def poll_company_info(self, company_id=0xFFFFFFFF):
		data = self.poll_info(
			types.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO,
			types.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_INFO,
			company_id
			)

		return self.parse_info_from_bytes(entities.Company, data)

	def poll_company_economy(self, company_id=0xFFFFFFFF):
		data = self.poll_info(
			types.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY,
			types.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_ECONOMY,
			company_id
			)

		return self.parse_info_from_bytes(entities.CompanyEconomy, data)

	def poll_company_stats(self, company_id=0xFFFFFFFF):
		data = self.poll_info(
			types.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS,
			types.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_STATS,
			company_id
			)

		return self.parse_info_from_bytes(entities.CompanyStats, data)


	def chat_external(self, source, user, message, color = 0):
		chat = PacketAdminChat()
		chat.chat_all_external(source, user, message, self.client_sock, color=color)

	def chat_all(self, message):
		chat = PacketAdminChat()
		chat.chat_all(message, self.client_sock)
		
	def chat_client(self, client_id, message):
		chat = PacketAdminChat()
		chat.chat_client( client_id, message, self.client_sock)

	def chat_company(self, company_id, message):
		chat = PacketAdminChat()
		chat.chat_company( company_id, message, self.client_sock)
	


	def disconnect(self):
		pass
