
import logging, time, inspect
from typing import Callable, Dict, List, Optional, Any, Union

from . import OTTDEnums


from .TCPSocket import TCPSocket
from .OTTDPacket import OTTDPacket
from .OTTDSendFactory import OTTDSendFactory
from .OTTDReceiveFactory import OTTDReceiveFactory


class MaxReconnectsException(Exception):
    def __init__(self, message = "Maximum reconnection attempts reached."):
        super().__init__(message)



class OTTDClient:
    logger: logging.Logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    allowed_frequencies = {
        OTTDEnums.AdminUpdateType.ADMIN_UPDATE_DATE: ( OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY, OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY),
        OTTDEnums.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO: ( OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY, OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC),
        OTTDEnums.AdminUpdateType.ADMIN_UPDATE_COMPANY_ECONOMY: ( OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY, OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY),
        OTTDEnums.AdminUpdateType.ADMIN_UPDATE_COMPANY_STATS: ( OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY, OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY),
    }


    def __init__(self, host: str, port: int, *, reconnect_delay_s: float = 5.0, max_reconnects: int = -1, logger: Optional[logging.Logger] = None):
        if logger is not None:
            self.logger = logger

        self.socket = TCPSocket(host, port, logger=self.logger)
        self.send_factory = OTTDSendFactory(logger=self.logger)
        self.receive_factory = OTTDReceiveFactory(logger=self.logger)
        
        self.is_logged_in = False
        self.subs: Dict[OTTDEnums.AdminUpdateType, OTTDEnums.AdminUpdateFrequency] = {}

        self.max_errors = 10
        self.error_count = 0

        self.is_reconnecting = False
        self.max_reconnects = max_reconnects
        self.reconnect_delay_s = reconnect_delay_s

        self.logger.info("Client initialized")
    

    def __reconnect__(self) -> bool:
        if self.is_reconnecting: return False

        self.is_reconnecting = True
        self.error_count = 0
        
        reconnect_attempts = 0
        while reconnect_attempts < self.max_reconnects:
            reconnect_attempts += 1
            self.logger.info(f"Reconnection attempt {reconnect_attempts}...")
            
            if self.socket.reconnect():
                self.logger.info("Reconnected successfully")
                break
            
            time.sleep(self.reconnect_delay_s)
        
        if not self.socket.is_connected():
            self.is_reconnecting = False
            raise MaxReconnectsException(f"Reconnection failed after {reconnect_attempts} attempts...")
        
        for packet_type, frequency in self.subs.items():
            if not self.subscribe(packet_type, frequency):
                self.is_reconnecting = False
                raise MaxReconnectsException("Failed to subscribe to updates after reconnection")

        self.is_reconnecting = False
        return True


    def __receive__(self, buffer_size: int = 4096, *, timeout_s: Optional[float] = 1, peek: bool = False):
        data = self.socket.receive(buffer_size, timeout_s=timeout_s, peek=peek)
        if data is not None:
            return data
                
        self.__reconnect__()            # handle reconnection
        return None


    def send(self, data: bytes) -> bool:
        if self.socket.send(data):
            return True
        
        self.__reconnect__()            # handle reconnection
        return False


    def receive(self):
        if self.error_count > self.max_errors:
            self.__reconnect__()
            return None
        
        packet_header = self.__receive__(3, timeout_s=1, peek=True)              # peek for packet
        if packet_header is None or len(packet_header) is 0:
            return None
        
        packet_type = OTTDPacket.get_packet_type(packet_header)
        packet_length = OTTDPacket.get_packet_length(packet_header)

        # Fatal error invalid packet_header: flush buffer and await new packet
        if packet_type is None or packet_length is None:
            self.socket.flush()
            self.error_count += 1
            return None
        
        # Fatal error invalid packet: flush buffer and await new packet
        packet_raw = self.__receive__( packet_length, timeout_s=30 )              # fetch packet if any
        if packet_raw is None or len(packet_raw) is not packet_length:
            self.socket.flush()
            self.error_count += 1
            return None
        
        self.error_count = 0
        packet_raw = bytearray(packet_raw)
        
        try:
            packet_factory = OTTDReceiveFactory.PACKET_FACTORY_MATCH[ packet_type ]
            if callable(packet_factory):
                return packet_factory(self.receive_factory, packet_raw)
            
            self.logger.error(f"Packet {packet_type.name} factory is not callable")
        except Exception as e:
            self.logger.error(f"Failed constructing packet of type {packet_type.name} from factory: Error: {e}")
        
        return None
    

    def join_game(self, admin_name, admin_password) -> bool:
        self.logger.info(f"Joining game with admin client: {admin_name}")

        pkt = self.send_factory.join_packet(admin_name, admin_password, "1.0.0")

        if not self.socket.connect() or not self.send(pkt):
            return False
        
        self.server_protocol = self.receive()
        self.server_welcome = self.receive()

        if not self.server_protocol or not self.server_welcome:
            self.logger.error( f"Failed to join the server..." )
            return False
        
        self.logger.info( f"Welcome to server: \n{self.server_welcome}" )

        self.is_logged_in = True

        return True
    

    # request packet update
    def poll(self, packet_type: OTTDEnums.AdminUpdateType, extra_data:int = OTTDEnums.MAX_UINT):
        if not self.is_logged_in: 
            return False
        
        pkt = self.send_factory.poll_packet(packet_type, extra_data=extra_data)
        return self.send( pkt.to_bytes() )
    

    # subscribe to packets
    def subscribe(self, packet_type: OTTDEnums.AdminUpdateType, frequency: OTTDEnums.AdminUpdateFrequency) -> bool:
        if packet_type in self.allowed_frequencies:
            min_freq, max_freq = self.allowed_frequencies[packet_type]
            resolved = max(min_freq, min(frequency, max_freq))
            if resolved != frequency:
                self.logger.warning(f"Preffering {resolved.name} for {packet_type.name} over requested {frequency.name}...")
                frequency = resolved

        if packet_type in self.subs:
            self.logger.warning(f"Already subscribed for {packet_type.name} at rate {self.subs[packet_type].name}. Requested rate {frequency.name}...")
            return True

        self.subs[packet_type] = frequency

        if not self.is_logged_in: 
            return True
        
        pkt = self.send_factory.update_packet(packet_type, frequency)
        return self.send( pkt.to_bytes() )
    

    # un-subscribe packet
    def unsubscribe(self, packet_type: OTTDEnums.AdminUpdateType):

        if packet_type not in self.subs:
            return True
        
        del self.subs[packet_type]
        
        if not self.is_logged_in:
            return False
		
        pkt = self.send_factory.update_packet(packet_type, OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_POLL)
        return self.send( pkt.to_bytes() )
    

    def ping(self) -> bool:
        pkt = self.send_factory.ping_packet()
        return self.send( pkt.to_bytes() )
    

    def chat_all(self, message):
        pkt = self.send_factory.chat_packet(OTTDEnums.CHAT_TYPE.ALL, message)
        self.send( pkt.to_bytes() )
    
    def chat_team(self, company_id, message):
        company_id -= 1			# zero base companies
        pkt = self.send_factory.chat_packet(OTTDEnums.CHAT_TYPE.COMPANY, message, to=company_id)
        self.send( pkt.to_bytes() )

    def chat_client(self, client_id, message):
        pkt = self.send_factory.chat_packet(OTTDEnums.CHAT_TYPE.CLIENT, message, to=client_id)
        self.send( pkt.to_bytes() )

    def chat_external(self, source, user, message, color = OTTDEnums.TextColor.TC_BLUE):
        pkt = self.send_factory.external_chat_packet(source, user, message, color)
        self.send( pkt.to_bytes() )
    
