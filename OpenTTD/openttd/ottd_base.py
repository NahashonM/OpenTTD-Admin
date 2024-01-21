
import logging

import openttd.ottd_enum as ottdenum
import openttd.ottd_packet as ottdpkt
import openttd.ottd_socket as ottdsocket


logger = logging.getLogger("OTTDBase")


class OttdBase:
	def __init__(self, server_ip, admin_port) -> None:
		self.sock = ottdsocket.OttdSocket(server_ip, admin_port)
		self.server_welcome = None
		self.server_protocol = None

		self.peek_retries = 3


	def join_server(self, admin_name, admin_password):

		pkt = ottdpkt.join_packet_factory(admin_name, admin_password, ottdenum.ADMIN_CLIENT_VERSION)

		self.sock.disconnect()
		self.sock.connect()

		self.send( pkt.to_bytes() )

		# self.server_protocol = self.receive(ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL)
		# self.server_welcome = self.receive(ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME)
		# return self.server_protocol, self.server_welcome
		


	def leave_server(self):
		pkt = ottdpkt.quit_packet_factory()
		self.send( pkt.to_bytes() )
		self.sock.disconnect()


	def ping_server(self):
		pkt = ottdpkt.ping_packet_factory()
		self.send( pkt.to_bytes() )


	def send(self, raw_data : bytearray):
		self.sock.send_data( raw_data )



	def receive(self):

		pkt_header = self.sock.peek(retries=self.peek_retries)

		if len(pkt_header) != 3:
			return None
		
		data_length = ottdpkt.get_packet_length(pkt_header)
		packet_type = ottdpkt.get_packet_type(pkt_header) 

		try:
			data = self.sock.receive_data(data_length)
			packet_factory = ottdpkt.PACKET_FACTORY_MATCH[ packet_type ]
			return packet_factory( data )
		
		except:
			logger.error(f"unmatched packet type {packet_type}")
			return None
		
	
	# RCON_CMDs also available from base class
	# 	base class however does not handle responses to rcon cmds
	#---------------------------------------------------------------
	def rcon_cmd(self, cmd):
		pkt = ottdpkt.rcon_packet_factory(cmd)
		self.send( pkt.to_bytes() )


	# Chat to game is available from base class
	#-------------------------------------------
	def chat_all(self, message):
		pkt = ottdpkt.chat_packet_factory(ottdenum.CHAT_TYPE.ALL, message)
		self.send( pkt.to_bytes() )
	

	def chat_team(self, company_id, message):
		company_id -= 1			# zero base companies
		pkt = ottdpkt.chat_packet_factory(ottdenum.CHAT_TYPE.COMPANY, message, to=company_id)
		self.send( pkt.to_bytes() )
	

	def chat_client(self, client_id, message):
		pkt = ottdpkt.chat_packet_factory(ottdenum.CHAT_TYPE.CLIENT, message, to=client_id)
		self.send( pkt.to_bytes() )


	def chat_external(self, source, user, message, color = ottdenum.TextColor.TC_BLUE):
		pkt = ottdpkt.external_chat_packet_factory(source, user, message, color)
		self.send( pkt.to_bytes() )
	