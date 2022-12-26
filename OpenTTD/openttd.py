

from OpenTTD.network.packet_types import PacketAdminJoin
from OpenTTD.network.packet_types import PacketServerWelcome
from OpenTTD.network.packet_types import PacketAdminChat
from OpenTTD.network.packet import Packet
import OpenTTD.enums as types


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

		join_packet = PacketAdminJoin(self.admin_name, self.admin_password, types.ADMIN_CLIENT_VERSION)
		
		self.client_sock.connect((self.server_ip, self.server_admin_port))

		with self.client_sock:
			join_packet.send_data(self.client_sock)

			raw_packet = Packet.receive_data( self.client_sock )

			if raw_packet.get_type() != types.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL:
				raise RuntimeError(f"Got {str(raw_packet.get_type())} when expecting PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL")
			
			srvr_protocol_packet = raw_packet

			raw_packet = Packet.receive_data( self.client_sock)
			if raw_packet.get_type() != types.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME:
				raise RuntimeError(f"Got {str(raw_packet.get_type())} when expecting PacketAdminType.ADMIN_PACKET_SERVER_WELCOME")

			srvr_welcome_packet = PacketServerWelcome(raw_packet)

			chat = PacketAdminChat()

			chat.chat_all( "all_message", 'All')
			chat.chat_client(1, "client_message", 'All')
			chat.chat_company(1, "company_message", 'All')

			chat.send_data(self.client_sock)

			print( chat.get_data() )


	def disconnect(self):
		pass

	def chat(self):
		pass