
import sys
import OpenTTD.enums as types
import OpenTTD.network.packet as packet

from OpenTTD.date import Date

class PacketAdminJoin( packet.Packet ):

	def __init__(self, admin_name: str, admin_password: str, app_version: str ) -> None:
		super().__init__( packet_type = types.PacketAdminType.ADMIN_PACKET_ADMIN_JOIN )

		self.add_str(admin_password)
		self.add_str(admin_name)
		self.add_str(app_version)
	
	def get_admin_name(self):
		data = self.get_data().split(b'\x00')
		return data[1].decode()

	def get_admin_password(self):
		data = self.get_data().split(b'\x00')
		return data[0].decode()

	def get_app_version(self):
		data = self.get_data().split(b'\x00')
		return data[2].decode()


class PacketServerWelcome( packet.Packet ):

	def __init__(self, raw_packet: packet.Packet ):
		if not isinstance(raw_packet, packet.Packet):
			raise RuntimeError("Expecting value of packet.Packet")

		super().__init__( packet_type=raw_packet.get_type(), packet_data=raw_packet.get_data() )

		print( self.get_data().split(b'\x00'))
	
	def get_server_name(self):
		return self.get_data().split(b'\x00')[0].decode()
	
	def get_server_version(self):
		return self.get_data().split(b'\x00')[1].decode()
	
	# dedicated server | etc
	def get_server_type(self):
		return bool(self.get_data().split(b'\x00')[2])
	
	# used to be map name
	def get_game_map_name(self):
		return self.get_data().split(b'\x00')[3].decode()
	
	def get_game_creation_seed(self):
		return int.from_bytes(self.get_data().split(b'\x00')[4], sys.byteorder, signed=False)

	def get_game_start_year(self):
		days = int.from_bytes(self.get_data().split(b'\x00')[5], sys.byteorder, signed=False)
		return Date.ConvertDateToYMD(days)
	
		
	def get_game_landscape(self):
		return int.from_bytes(self.get_data().split(b'\x00')[6], sys.byteorder, signed=False)
	
	def get_game_map_size(self):
		x = int.from_bytes(self.get_data().split(b'\x00')[7], sys.byteorder)
		y = int.from_bytes(self.get_data().split(b'\x00')[8], sys.byteorder)
		return (x, y)
	

class PacketAdminChat(packet.Packet):
	def __init__(self, *, chat_type=types.NetworkAction.NETWORK_ACTION_CHAT, packet_data=b''):
		if not packet_data:
			super().__init__(packet_type=types.PacketAdminType.ADMIN_PACKET_ADMIN_CHAT)

			self.add_int(types.NetworkAction.NETWORK_ACTION_CHAT_COMPANY, 1, separator=b'')
			self.add_int(types.NetworkAction.NETWORK_ACTION_CHAT_CLIENT, 1, separator=b'')
		
		else:
			super.__init__(packet_data=packet_data)

	def chat_all(self, message, scope):
		self.add_int(types.NetworkAction.NETWORK_ACTION_CHAT, 1, separator=b'')
		self.add_int(types.NetworkAction.NETWORK_ACTION_CHAT, 1, separator=b'')

		self.add_int(0, 4, separator=b'')
		self.add_str(message, separator=b'')

	
	def chat_client(self, client_id, message, scope):
		self.add_int(types.NetworkAction.NETWORK_ACTION_CHAT_CLIENT, 1, separator=b'')
		self.add_int(types.NetworkAction.NETWORK_ACTION_CHAT_CLIENT, 1, separator=b'')

		self.add_int(client_id, 4, separator=b'')
		self.add_str(message, separator=b'')


	def chat_company(self, company_id, message, scope):
		self.add_int(types.NetworkAction.NETWORK_ACTION_CHAT_COMPANY, 1, separator=b'')
		self.add_int(types.NetworkAction.NETWORK_ACTION_CHAT_COMPANY, 1, separator=b'')

		self.add_int(company_id, 4, separator=b'')
		self.add_str(message, separator=b'')