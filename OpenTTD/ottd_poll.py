import time
import threading

import ottd_enum as ottdenum
import ottd_packet as ottdpkt

from ottd_base import OttdBase


class OttdPoll(OttdBase):
	
	def __init__(self, server_ip, admin_port) -> None:
		super().__init__(server_ip, admin_port)

		pass
	

	def __del__(self):
		pass

	
	def __poll_info__(self, info_type, extra_data, receive_type):

		pkt = ottdpkt.poll_packet_factory(info_type, extra_data=extra_data)

		self.send( pkt.to_bytes() )

		elapsed_time = 0
		start_time = time.time()

		while elapsed_time < 10:
			data = None

			if extra_data == ottdenum.MAX_UINT:
				data = self.receive_list( receive_type )
			else:
				data = self.receive( receive_type )

			if data: 
				return data
			
			elapsed_time = time.time() - start_time
		
		return None
			
	
	
	def poll_company_remove_reason(self):
		return self.receive(ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_REMOVE)



	def poll_current_date(self) -> tuple:
		return self.__poll_info__(ottdenum.AdminUpdateType.ADMIN_UPDATE_DATE, 0, ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_DATE)




	def poll_client_info(self, client_id=ottdenum.MAX_UINT) -> tuple:
		return self.__poll_info__(ottdenum.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, client_id, ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_CLIENT_INFO)




	def poll_company_info(self, company_id=ottdenum.MAX_UINT) -> tuple:
		return self.__poll_info__(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, company_id, ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_INFO)
	



	def poll_company_economy(self, company_id=ottdenum.MAX_UINT) -> tuple:
		return self.__poll_info__(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY, company_id, ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_ECONOMY)




	def poll_company_stats(self, company_id=ottdenum.MAX_UINT) -> tuple:
		return self.__poll_info__(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS, company_id, ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_STATS)
	
