import socket
import time
import logging
from typing import Optional


class TCPSocket:
    logger: logging.Logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    
    def __init__(self, host: str, port: int, *, logger: Optional[logging.Logger] = None):
        self.host = host
        self.port = port

        self.default_timeout_s: float = 5

        self.socket: Optional[socket.socket] = None
        
        if logger is not None:
            self.logger = logger
        

    def connect(self, timeout_s: Optional[float] = None) -> bool:
        try:
            if self.socket:
                self.socket.close()
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout_s or self.default_timeout_s)
            self.socket.connect((self.host, self.port))
            
            self.logger.info(f"Connected to {self.host}:{self.port}")
            return True
                
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

            self.socket = None

        self.logger.info("Disconnected from server")
    

    def is_connected(self) -> bool:
        try:
            self.socket.setblocking(False)

            try:
                data = self.socket.recv(1, socket.MSG_PEEK)
                return True if len(data) > 0 or isinstance(data, (bytes, bytearray)) else False
            except socket.error as e:
                return True if e.errno in (socket.EAGAIN, socket.EWOULDBLOCK) else False
            
        except Exception as e:
            return False
        finally:
            try:
                self.socket.setblocking(True)
            except:
                pass


    def reconnect(self, *, reconnect_delay_s: float = 5.0, max_reconnect_attempts: int = -1) -> bool:
        if self.is_connected():
            return True
        
        reconnect_attempts = 0
        while reconnect_attempts < max_reconnect_attempts:
            reconnect_attempts += 1
            self.logger.info(f"Reconnection attempt {reconnect_attempts}...")
            
            if self.connect():
                self.logger.info("Reconnected successfully")
                return True
            
            time.sleep(reconnect_delay_s)

        self.logger.error(f"Reconnection failed after {reconnect_attempts} attempts...")
        return False
    
    
    def send(self, data: bytes) -> bool:
        if not self.is_connected():
            self.logger.error("Cannot send: connection lost")
            return False
        
        try:
            self.socket.sendall(data)
        except Exception as e:
            self.logger.error(f"Send failed: {e}")
            return False
        
        if not self.is_connected():
            self.logger.warning("Possibly incomplete data sent. Connection lost..")
            return False
        
        return True
    

    def receive(self, buffer_size: int = 4096, *, timeout_s: Optional[float] = None, peek = False) -> Optional[bytes]:
        data = b''

        try:
            self.socket.settimeout(timeout_s or self.default_timeout_s)
            data = self.socket.recv(buffer_size, socket.MSG_PEEK if peek else 0)
        except BlockingIOError:
            pass
        except socket.timeout:
            pass
        except Exception as e:
            self.logger.error(f"Receive failed: {e}")
            return None
        
        if not self.is_connected():
            self.logger.warning("Possibly corrupt data received. Connection lost...")
            return None
        
        return data
    

    def flush(self):
        try:
            self.socket.setblocking(False)

            try:
                while True:
                    data = self.socket.recv(4096)
                    if not data:
                        break
            except socket.error as e:
                return True if e.errno in (socket.EAGAIN, socket.EWOULDBLOCK) else False
            
        except Exception as e:
            return False
        finally:
            try:
                self.socket.setblocking(True)
            except:
                pass

