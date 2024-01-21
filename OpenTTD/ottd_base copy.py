
import logging

import OpenTTD.openttd.ottd_enum as ottdenum
import OpenTTD.openttd.ottd_packet as ottdpkt
import OpenTTD.openttd.ottd_socket as ottdsocket


logger = logging.getLogger("OttdBase")


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

		self.server_protocol = self.receive(ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL)
		self.server_welcome = self.receive(ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME)

		return self.server_protocol, self.server_welcome
		


	def leave_server(self):

		pkt = ottdpkt.quit_packet_factory()

		self.send( pkt.to_bytes() )

		self.sock.disconnect()



	def ping_server(self):
		pkt = ottdpkt.ping_packet_factory()

		self.send( pkt.to_bytes() )

		pong = self.receive( ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_PONG )

		if pong == None:
			return False
		
		return True



	def send(self, raw_data : bytearray):
		self.sock.send_data( raw_data )



	# return true if now at search packet
	# return false if empty buffer of invalid packet
	def misc_mode(self, search_pkt, unexpected_pkt_handler):
		# init so we check at least once
		pkt = 1

		while pkt != None:
			pkt_header = self.sock.peek(retries=self.peek_retries)

			# invalid packet
			if len(pkt_header) != 3: return False

			# found expected packet
			if ottdpkt.get_packet_type(pkt_header) == search_pkt: return True	
			
			pkt = self.receive_any()
			unexpected_pkt_handler(pkt)
		
		# no more data in buffer
		return False
	


	def receive(self, packet_type, *, unexpected_pkt_handler = None):

		pkt_header = self.sock.peek(retries=self.peek_retries)

		if len(pkt_header) != 3:
			return None
		
		# try to search for packet
		if ottdpkt.get_packet_type(pkt_header) != packet_type:
			if unexpected_pkt_handler == None or not self.misc_mode(packet_type, unexpected_pkt_handler):
				return None
			
			# get packet info again
			pkt_header = self.sock.peek(retries=self.peek_retries)
			if len(pkt_header) != 3: 
				return None
		
		data_length = ottdpkt.get_packet_length(pkt_header)
		data = self.sock.receive_data(data_length)

		packet_factory = ottdpkt.PACKET_FACTORY_MATCH[ packet_type ]
		return packet_factory( data )



	def receive_list(self, packet_type, *, unexpected_pkt_handler = None):
		data = list()
		tmp = self.receive(packet_type, unexpected_pkt_handler = unexpected_pkt_handler)

		while tmp is not None:
			data.append(tmp)
			tmp = self.receive(packet_type, unexpected_pkt_handler = unexpected_pkt_handler)
		
		return data
	
	

	def receive_any(self):

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
		



	def flush_buffer(self):
		packets = []
		any_packet = self.receive_any()

		while any_packet != None:
			packets.append( any_packet )
			any_packet = self.receive_any()
		
		return packets
		
	
	
	def rcon_cmd(self, cmd):
		pkt = ottdpkt.rcon_packet_factory(cmd)
		self.send( pkt.to_bytes() )

		rcon_res = self.receive_list( ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_RCON )
		rcon_end = self.receive( ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_RCON_END )

		return rcon_res, rcon_end



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
	