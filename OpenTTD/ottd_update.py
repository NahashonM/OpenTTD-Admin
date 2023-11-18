import time

import ottd_util as util
import ottd_enum as ottdenum
import ottd_packet as ottdpkt

from ottd_base import OttdBase


class OttdUpdate(OttdBase):
	def __init__(self, server_ip, admin_port) -> None:
		super().__init__(server_ip, admin_port)

		self.registered_updates = list()


	def __request_update__(self, info_type: ottdenum.AdminUpdateType, frequency ):

		if info_type in self.registered_updates:
			return True

		self.registered_updates.append(info_type)

		pkt = ottdpkt.update_frequency_packet_factory(info_type, frequency)
		
		return self.send( pkt.to_bytes() )
	
	
	def __stop_update__(self, info_type):
		if info_type not in self.registered_updates:
			return True
		
		pkt = ottdpkt.update_frequency_packet_factory(info_type, ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_POLL)

		status = self.send( pkt.to_bytes() )
		
		self.registered_updates.remove(info_type)

		return status
		
	

	# clamp Daily - anually
	def request_date_updates(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY) -> bool:
		frequency = max(ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY, min(frequency, ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY))
		return self.__request_update__( ottdenum.AdminUpdateType.ADMIN_UPDATE_DATE, frequency)

	def stop_date_update(self):
		return self.__stop_update__(ottdenum.AdminUpdateType.ADMIN_UPDATE_DATE)
	


	# clamp Daily - automatic
	def request_client_info_updates(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		frequency = max(ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY, min(frequency, ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC))
		return self.__request_update__( ottdenum.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, frequency)
	
	def stop_client_info_update(self):
		return self.__stop_update__(ottdenum.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO)
	


	# Only Automatic
	def request_company_info_updates(self) -> bool:
		return self.__request_update__( ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC)
	
	def stop_company_info_update(self):
		return self.__stop_update__(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO)
	


	# clamp weekly - anually
	def request_company_economy_updates(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY) -> bool:
		frequency = max(ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY, min(frequency, ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY))
		return self.__request_update__( ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY, frequency)
	
	def stop_company_economy_update(self):
		return self.__stop_update__(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY)
	


	# clamp weekly - anually
	def request_company_stats_updates(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY ) -> bool:
		frequency = max(ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY, min(frequency, ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY))
		return self.__request_update__( ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS, frequency)
	
	def stop_company_stats_update(self):
		return self.__stop_update__(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS)
	



	def request_chat_updates(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__request_update__( ottdenum.AdminUpdateType.ADMIN_UPDATE_CHAT, frequency)
	
	def stop_chat_update(self):
		return self.__stop_update__(ottdenum.AdminUpdateType.ADMIN_UPDATE_CHAT)
	


	def request_console_updates(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__request_update__( ottdenum.AdminUpdateType.ADMIN_UPDATE_CONSOLE, frequency)
	
	def stop_console_update(self):
		return self.__stop_update__(ottdenum.AdminUpdateType.ADMIN_UPDATE_CONSOLE)
	



	def request_cmd_names_updates(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__request_update__( ottdenum.AdminUpdateType.ADMIN_UPDATE_CMD_NAMES, frequency)

	def stop_cmd_update(self):
		return self.__stop_update__(ottdenum.AdminUpdateType.ADMIN_UPDATE_CMD_NAMES)
	



	def request_cmd_logging_updates(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__request_update__( ottdenum.AdminUpdateType.ADMIN_UPDATE_CMD_LOGGING, frequency)

	def stop_cmd_logging_update(self):
		return self.__stop_update__(ottdenum.AdminUpdateType.ADMIN_UPDATE_CMD_LOGGING)
	


	def request_gamescript_updates(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
		return self.__request_update__( ottdenum.AdminUpdateType.ADMIN_UPDATE_GAMESCRIPT, frequency)

	def stop_cmd_logging_update(self):
		return self.__stop_update__(ottdenum.AdminUpdateType.ADMIN_UPDATE_CMD_LOGGING)
	



	def get_update(self):
		return self.receive_any()

