import time
import threading
import logging


import ottd_enum as ottdenum
import ottd_packet as ottdpkt

from ottd_base import OttdBase


logger = logging.getLogger("OttdPoll_Admin")


class OttdPoll(OttdBase):
	
	def __init__(self, server_ip, admin_port) -> None:
		super().__init__(server_ip, admin_port)

		self.buffer_lock = threading.Semaphore()

		self.svr_state_thread = threading.Thread(target=self.__svr_state_handler__)
		self.svr_state_thread.start()


	def __svr_state_handler__(self):
		# start thread delayed
		time.sleep(2)

		while(True):
			# acquire buffer lock
			self.buffer_lock.acquire()

			# get all packets in buffer
			packets = []
			any_packet = self.receive_any()

			while any_packet != None:
				packets.append( any_packet )
				any_packet = self.receive_any()
			
			# release buffer lock
			self.buffer_lock.release()
			
			# Handle received packets
			if packets:
				for pkt in packets:
					self.orderless_packet_handler(pkt)

			# go back to sleep
			time.sleep(1)
	

	def orderless_packet_handler(self, packet):
		# TODO handle packets or register handler
		# for now the updateAdmin handles them so s ignored
		# Ability to register callbacks for these events would be great for
		#  making this class fully capable on its own just as the continuos update client
		logger.warn("Unimplemented packet handling for orderless_packet_handler")
	

	def rcon_cmd(self, cmd):
		self.buffer_lock.acquire()

		super().rcon_cmd(cmd)
		
		self.buffer_lock.release()


	
	def __poll_info__(self, info_type, extra_data, receive_type):
		self.buffer_lock.acquire()

		pkt = ottdpkt.poll_packet_factory(info_type, extra_data=extra_data)

		self.send( pkt.to_bytes() )

		elapsed_time = 0
		start_time = time.time()

		while elapsed_time < 10:
			data = None

			if extra_data == ottdenum.MAX_UINT:
				data = self.receive_list( receive_type, unexpected_pkt_handler = self.orderless_packet_handler )
			else:
				data = self.receive( receive_type, unexpected_pkt_handler = self.orderless_packet_handler )

			if data: 
				# release buffer lock and return
				self.buffer_lock.release()
				return data
			
			elapsed_time = time.time() - start_time
		
		# release buffer lock 
		self.buffer_lock.release()
		return None
			
	
	
	def poll_company_remove_reason(self):
		self.buffer_lock.acquire()
		data = self.receive(ottdenum.PacketAdminType.ADMIN_PACKET_SERVER_COMPANY_REMOVE, unexpected_pkt_handler = self.orderless_packet_handler )
		self.buffer_lock.release()

		return data



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
	
