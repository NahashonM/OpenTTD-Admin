
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

    def __init__(self, server_ip, admin_port):

        super().__init__(server_ip, admin_port)

        self.pkt_handlers = {}
        self.registered_auto_updates = []

        self.is_ready = False
    

    def set_is_ready(self, ready):
        self.is_ready = ready

    # return:
    #   bool [False: Failed, True: Success]
    def poll(self, info_type, extra_data):
        if not self.is_ready:
            return False
        
        pkt = ottdpkt.poll_packet_factory(info_type, extra_data=extra_data)
        return self.send( pkt.to_bytes() )
    

    # Name:
    #   request_auto_update
    #
    # Purpose:
    #   Request openttd to send automatic updates or adjust the update frequency.
    #
    # Return
    #     True : successfully registered
    #     False: failed to register request
    def request_auto_update(self, info_type: ottdenum.AdminUpdateType, frequency): 
        if not self.is_ready:
            return False 

        #---- clamp stat update windows
        if info_type == ottdenum.AdminUpdateType.ADMIN_UPDATE_DATE:
            frequency = max(ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY, min(frequency, ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY)) 

        elif info_type == ottdenum.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO:
            frequency = max(ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY, min(frequency, ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC)) 

        elif info_type == ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY or info_type == ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS:
            frequency = max(ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY, min(frequency, ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY))
        
        if info_type not in self.registered_auto_updates:
            self.registered_auto_updates.append(info_type) 

        pkt = ottdpkt.update_frequency_packet_factory(info_type, frequency)

        return self.send( pkt.to_bytes() )
    

    # Name:
    #   stop_auto_update
    #
    # Purpose:
    #
    #
    # Return
    #     True : successfully un-registered or not registered
    #     False: Failed to un-register
    def stop_auto_update(self, info_type):
        if not self.is_ready:
            return False
        
        if info_type not in self.registered_auto_updates:
            return True
		
        pkt = ottdpkt.update_frequency_packet_factory(info_type, ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_POLL)
        status = self.send( pkt.to_bytes() )

        if status:
            self.registered_auto_updates.remove(info_type)
        
        return status
    

    # Name:
    #   register_pkt_handler
    #
    # Purpose:
    #   Register handlers for packets sent by openttd
    #
    # Params:
    #   callcount:
    #           -1 unlimited
    #           n > 0 call n times
    #
    # Return
    #     True : successfully registered
    #     False: Failed to register
    def register_pkt_handler(self, packet_name, handler, *, call_count = -1, args = None):

        if call_count == 0:
            return False

        try:
            if packet_name not in self.pkt_handlers:
                self.pkt_handlers[packet_name] = {}
            
            handler_id = str(uuid.uuid4())

            if args == None:
                self.pkt_handlers[packet_name][handler_id] = {
                                                                "handler": handler, 
                                                                "call_count": call_count
                                                            }
            else:
                self.pkt_handlers[packet_name][handler_id] = {
                                                            "handler": handler, 
                                                            "call_count": call_count,
                                                            "args": args,
                                                        }

            return handler_id
        except:
            pass

        return None
        

    def unregister_pkt_handler(self, packet_name, handler_id):

        if  packet_name not in self.pkt_handlers: 
            return True
        
        if  handler_id not in self.pkt_handlers[packet_name]:  
            return True

        try:
            del self.pkt_handlers[packet_name][handler_id]

            if len(self.pkt_handlers[packet_name]) < 1: 
                del self.pkt_handlers[packet_name]
        except:
            return False

        return True
    
    

    # blocking
    def run(self):
        while self.is_ready:

            pkt = self.receive()
            
            if pkt != None:
                packet_name = type(pkt).__name__

                if packet_name not in self.pkt_handlers:
                    logger.warn(f'Unhandled packet {packet_name}')
                    continue

                try:
                    marked_handlers = list()
                    
                    for handler_id in self.pkt_handlers[ packet_name ]:
                        if 'args' in self.pkt_handlers[ packet_name ][ handler_id ]:
                            args = self.pkt_handlers[ packet_name ][ handler_id ]["args"]
                            self.pkt_handlers[ packet_name ][ handler_id ]["handler"](pkt, args)
                        else:
                            self.pkt_handlers[ packet_name ][ handler_id ]["handler"](pkt)


                        if self.pkt_handlers[ packet_name ][ handler_id ]["call_count"] > 0:
                            self.pkt_handlers[ packet_name ][ handler_id ]["call_count"] -= 1

                            if self.pkt_handlers[ packet_name ][ handler_id ]["call_count"] == 0:
                                marked_handlers.append(handler_id)

                    # clean up packet handlers  
                    for handler_id in marked_handlers:
                        del self.pkt_handlers[ packet_name ][ handler_id ]

                except Exception as e:
                    logger.error( f"An exception occurred handling packet {packet_name}. {e}." )

            # cool down
            time.sleep(1)


    #----------------------------------------------------
    #------------- Poll functions ---------------------
    #----------------------------------------------------
    def poll_current_date(self) -> tuple:
        return self.poll(ottdenum.AdminUpdateType.ADMIN_UPDATE_DATE, 0 )
    
    def poll_client_info(self, client_id=ottdenum.MAX_UINT) -> tuple:
        return self.poll(ottdenum.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, client_id)
    
    def poll_company_info(self, company_id=ottdenum.MAX_UINT) -> tuple:
        return self.poll(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, company_id)
    
    def poll_company_economy(self, company_id=ottdenum.MAX_UINT) -> tuple:
        return self.poll(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY, company_id)
    
    def poll_company_stats(self, company_id=ottdenum.MAX_UINT) -> tuple:
        return self.poll(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS, company_id)
	

    #--------------------------------------------------
    #--------- Update Reqest functions ----------------
    #--------------------------------------------------
    # clamp Daily - anually
    def request_auto_update_date(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY) -> bool:
        return self.request_auto_update( ottdenum.AdminUpdateType.ADMIN_UPDATE_DATE, frequency)

    def stop_date_update(self):
        return self.stop_auto_update(ottdenum.AdminUpdateType.ADMIN_UPDATE_DATE)


    # clamp Daily - automatic
    def request_auto_update_client_info(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
        return self.request_auto_update( ottdenum.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, frequency)

    def stop_client_info_update(self):
        return self.stop_auto_update(ottdenum.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO)


    # Only Automatic
    def request_auto_update_company_info(self) -> bool:
        return self.request_auto_update( ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC)

    def stop_company_info_update(self):
        return self.stop_auto_update(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO)

    # clamp weekly - anually
    def request_auto_update_company_economy(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY) -> bool:
        return self.request_auto_update( ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY, frequency)

    def stop_company_economy_update(self):
        return self.stop_auto_update(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY)


    # clamp weekly - anually
    def request_auto_update_company_stats(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY ) -> bool:
        return self.request_auto_update( ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS, frequency)

    def stop_company_stats_update(self):
        return self.stop_auto_update(ottdenum.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS)


    def request_auto_update_chat(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
        return self.request_auto_update( ottdenum.AdminUpdateType.ADMIN_UPDATE_CHAT, frequency)

    def stop_auto_update_chat(self):
        return self.stop_auto_update(ottdenum.AdminUpdateType.ADMIN_UPDATE_CHAT)
    

    def request_auto_update_console(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
        return self.request_auto_update( ottdenum.AdminUpdateType.ADMIN_UPDATE_CONSOLE, frequency)

    def stop_auto_update_console(self):
        return self.stop_auto_update(ottdenum.AdminUpdateType.ADMIN_UPDATE_CONSOLE)


    def request_auto_update_cmd_names(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
        return self.request_auto_update( ottdenum.AdminUpdateType.ADMIN_UPDATE_CMD_NAMES, frequency)

    def stop_auto_update_cmd_names(self):
        return self.stop_auto_update(ottdenum.AdminUpdateType.ADMIN_UPDATE_CMD_NAMES)
    

    def request_auto_update_cmd_logging(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
        return self.request_auto_update( ottdenum.AdminUpdateType.ADMIN_UPDATE_CMD_LOGGING, frequency)

    def stop_auto_update_cmd_logging(self):
        return self.stop_auto_update(ottdenum.AdminUpdateType.ADMIN_UPDATE_CMD_LOGGING)


    def request_auto_update_gamescript(self, frequency = ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
        return self.request_auto_update( ottdenum.AdminUpdateType.ADMIN_UPDATE_GAMESCRIPT, frequency)

    def stop_auto_update_gamescript(self):
        return self.stop_auto_update(ottdenum.AdminUpdateType.ADMIN_UPDATE_GAMESCRIPT)



