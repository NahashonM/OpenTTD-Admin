
import sys
import socket
import OpenTTD.enums as types

from OpenTTD.network.packet import Packet
from OpenTTD.date import Date


#----------------------------------------------
#		ADMIN_PACKET_ADMIN_JOIN
#----------------------------------------------
class PacketAdminJoin( Packet ):

	def __init__(self, admin_name: str, admin_password: str, app_version: str ) -> None:
		self.admin_password = admin_password
		self.admin_name = admin_name
		self.app_version = app_version
	
	def send_data(self, tcp_socket: socket.socket) -> bool:

		data = Packet.str_to_bytes(self.admin_password )
		data += Packet.str_to_bytes(self.admin_name )
		data += Packet.str_to_bytes(self.app_version )

		return Packet.send_data(
			types.PacketAdminType.ADMIN_PACKET_ADMIN_JOIN, 
			data, 
			tcp_socket)
	
	def receive_data(self):
		raise RuntimeError(f"This packet type, {self} can only send data")



#----------------------------------------------
#		ADMIN_PACKET_SERVER_PROTOCOL
#----------------------------------------------
class PacketServerProtocol( Packet ):

	def __init__(self):
		self.server_name = ''
	
	def send_data(self):
		raise RuntimeError(f"This packet type, {self} can only receive data")
	
	def receive_data(self, tcp_socket: socket.socket) -> bool:
		packet_type, raw_data = Packet.receive_data(tcp_socket)

		if packet_type != types.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL:
			raise RuntimeError(f"Got {packet_type} when expecting {types.PacketAdminType.ADMIN_PACKET_SERVER_PROTOCOL}")




#----------------------------------------------
#		ADMIN_PACKET_SERVER_WELCOME
#----------------------------------------------
class PacketServerWelcome( Packet ):

	def __init__(self):
		pass
	
	def send_data(self):
		raise RuntimeError(f"This packet type, {self} can only receive data")
	
	def receive_data(self, tcp_socket: socket.socket) -> bool:
		packet_type, raw_data = Packet.receive_data(tcp_socket)

		if packet_type != types.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME:
			raise RuntimeError(f"Got {packet_type} when expecting {types.PacketAdminType.ADMIN_PACKET_SERVER_WELCOME}")

		index = 0
		length = 0
		
		self.server_name, length = Packet.get_str_from_bytes( raw_data[index:] )			; index += length
		self.server_version, length = Packet.get_str_from_bytes(  raw_data[index:] )		; index += length
		game_type, length = Packet.get_int_from_bytes(  raw_data[index:], 1)			; index += length
		self.game_type = types.ServerGameType(game_type)


		self.map_name, length = Packet.get_str_from_bytes(  raw_data[index:] )			; index += length
		self.generation_seed, length = Packet.get_int_from_bytes(  raw_data[index:], 4)	; index += length
		self.landscape, length = Packet.get_int_from_bytes(  raw_data[index:], 1)			; index += length
		self.start_year, length = Packet.get_int_from_bytes(  raw_data[index:], 4)		; index += length

		self.start_year = Date.ConvertDateToYMD( self.start_year ) 

		map_x, length = Packet.get_int_from_bytes(  raw_data[index:], 2)	; index += length
		map_y, _ = Packet.get_int_from_bytes(  raw_data[index:], 2)
		self.map_size = (map_x, map_y)


#----------------------------------------------
#		ADMIN_PACKET_ADMIN_CHAT
#----------------------------------------------
class PacketAdminChat(Packet):

	def is_valid_color( color):
		if not (color & types.TextColor.TC_IS_PALETTE_COLOUR):
			return types.TextColor.TC_BEGIN <= color and color < types.TextColor.TC_END
		
		return False


	def chat_all_external(self, source, user, message, tcp_socket, *, color = 0):
		data = b''

		data += Packet.str_to_bytes(source)				# source
		data += Packet.int_to_bytes(color, 2, separator=b'')	# color
		data += Packet.str_to_bytes(user)						# user
		data += Packet.str_to_bytes(message)

		Packet.send_data( types.PacketAdminType.ADMIN_PACKET_ADMIN_EXTERNAL_CHAT, data, tcp_socket)

	def chat_all(self, message, tcp_socket):
		data = b''

		data += Packet.int_to_bytes(types.NetworkAction.NETWORK_ACTION_CHAT, 1, separator=b'')
		data += Packet.int_to_bytes(types.DestType.DESTTYPE_BROADCAST, 1, separator=b'')
		data += Packet.int_to_bytes( 0, 4, separator=b'')
		data += Packet.str_to_bytes(message)

		Packet.send_data( types.PacketAdminType.ADMIN_PACKET_ADMIN_CHAT, data, tcp_socket)

	
	def chat_client(self, client_id, message, tcp_socket):
		data = b''

		data += Packet.int_to_bytes(types.NetworkAction.NETWORK_ACTION_CHAT_CLIENT, 1, separator=b'')
		data += Packet.int_to_bytes(types.DestType.DESTTYPE_CLIENT, 1, separator=b'')
		data += Packet.int_to_bytes(client_id, 4, separator=b'')
		data += Packet.str_to_bytes(message)

		Packet.send_data( types.PacketAdminType.ADMIN_PACKET_ADMIN_CHAT, data, tcp_socket)


	def chat_company(self, company_id, message, tcp_socket):
		data = b''

		data += Packet.int_to_bytes(types.NetworkAction.NETWORK_ACTION_CHAT_COMPANY, 1, separator=b'')
		data += Packet.int_to_bytes(types.DestType.DESTTYPE_TEAM, 1, separator=b'')
		data += Packet.int_to_bytes(company_id, 4, separator=b'')
		data += Packet.str_to_bytes(message)

		Packet.send_data( types.PacketAdminType.ADMIN_PACKET_ADMIN_CHAT, data, tcp_socket)




#----------------------------------------------
#		ADMIN_PACKET_ADMIN_POLL
#----------------------------------------------
class PacketAdminPoll(Packet):

	def poll(self, update_Type: types.AdminUpdateType, tcp_socket, *, extra_data:int = 0xFFFFFFFF):
		data = b''

		data += Packet.int_to_bytes( update_Type, 1, separator=b'')
		data += Packet.int_to_bytes( extra_data, 4, separator=b'')

		Packet.send_data( types.PacketAdminType.ADMIN_PACKET_ADMIN_POLL, data, tcp_socket)


#----------------------------------------------
#		DUMMY_PACKET
#----------------------------------------------

class DummyPacket(Packet):

	def receive_data(self, tcp_socket) -> tuple:
		self.packet_type, self.data =  Packet.receive_data(tcp_socket)
		self.packet_type = types.PacketAdminType(self.packet_type)
	
	def get_data(self):
		return self.data

	def get_type(self):
		return self.packet_type
		