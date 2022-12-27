

from OpenTTD.network.packet_types import PacketAdminJoin
from OpenTTD.network.packet_types import PacketServerWelcome
from OpenTTD.network.packet_types import PacketAdminChat
from OpenTTD.network.packet_types import PacketServerProtocol
from OpenTTD.network.packet_types import PacketAdminPoll
from OpenTTD.network.packet_types import DummyPacket
from OpenTTD.network.packet import Packet
from OpenTTD.entities import Client
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
		

	def server_listen(self):
		d = DummyPacket()
		d.receive_data(self.client_sock)
		return d.data
	

	def parse_client_infor_from_bytes(self, bytes_data):
		i = 0
		clients = list()
		while i < len(bytes_data):
			client = Client()
			i += client.parse_from_bytearray(bytes_data[i:])

			clients.append(client)
		
		return clients
	

	def poll_client_infor(self, client_id=0xFFFFFFFF):
		poll_packet = PacketAdminPoll()
		poll_packet.poll(types.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, self.client_sock, extra_data=client_id)

		data = b''
		d = DummyPacket()

		i = 1
		if client_id == 0xFFFFFFFF:
			i = 0

		while i < 2:
			d.receive_data(self.client_sock)

			if d.get_type() != types.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO:
				raise RuntimeError(f"Got {d.get_type()} when expecting PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO")
			
			data += d.get_data()
			i += 1

		return self.parse_client_infor_from_bytes(data)


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
