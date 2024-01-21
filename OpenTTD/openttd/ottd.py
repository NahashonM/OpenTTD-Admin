
import time
import signal
import threading
import logging
import uuid

from openttd.ottd_base import OttdBase

import openttd.ottd_enum as ottdenum
import openttd.ottd_packet as ottdpkt

logger = logging.getLogger("OpenTTD")


'''
    poll_mode   :   [ True | False]
                        True: only the poll methods can be used
                        False: only the update methods can be used
    
    Either way a thread will 
'''
class OpenTTD(OttdBase):

    def __init__(self, server_ip, admin_port, *, poll_mode = False):

        super().__init__(server_ip, admin_port)

        self.handlers = {}
        self.registered_updates = []

        self.poll_mode = poll_mode
        self.running = True
    


    def __poll_info__(self, info_type, extra_data):
        pkt = ottdpkt.poll_packet_factory(info_type, extra_data=extra_data)
        self.send( pkt.to_bytes() )

    
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
    

    def register_pkt_handler(self, packet, handler):

        try:
            if  packet not in self.handlers:
                self.handlers[packet] = {}
            
            handler_id = str(uuid.uuid4())
            self.handlers[packet][handler_id] = handler

            return handler_id
        except:
            pass

        return None
        

    def unregister_pkt_handler(self, packet, handler_id):

        if  packet not in self.handlers: 
            return False
        
        if  handler_id not in self.handlers[packet]:  
            return False

        try:
            del self.handlers[packet][handler_id]

            if len(self.handlers[packet]) < 1: 
                del self.handlers[packet]
        except:
            pass

        return True
    
    
    # blocking
    def run(self):
        while self.running:

            pkt = self.receive()
            
            while pkt != None:
                packet_type = type(pkt).__name__

                try:
                    for handler in self.handlers[ packet_type ]:
                        self.handlers[ packet_type ][ handler ](pkt)

                except KeyError:
                    logger.warn( f"Received unhandled packet {packet_type}" )
                
                pkt = self.receive()

            # cool down
            time.sleep(1)

    #----------------------------------------------------
    #------------- Poll functions ---------------------
    #----------------------------------------------------
    def poll_current_date(self) -> tuple:
        return self.__poll_info__(ottdenum.AdminUpdateType.ADMIN_UPDATE_DATE, 0 )
    
    def poll_client_info(self, client_id=ottdenum.MAX_UINT) -> tuple:
        return self.__poll_info__(ottdenum.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, client_id)
    
    def poll_company_info(self, company_id=ottdenum.MAX_UINT) -> tuple:
        return self.__poll_info__(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, company_id)
    
    def poll_company_economy(self, company_id=ottdenum.MAX_UINT) -> tuple:
        return self.__poll_info__(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY, company_id)
    
    def poll_company_stats(self, company_id=ottdenum.MAX_UINT) -> tuple:
        return self.__poll_info__(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS, company_id)
	

    #--------------------------------------------------
    #--------- Update Reqest functions ----------------
    #--------------------------------------------------
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



