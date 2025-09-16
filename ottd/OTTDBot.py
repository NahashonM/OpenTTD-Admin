import asyncio
import logging, time, inspect
from typing import Callable, Dict, List, Optional, Any, Union
import inspect

from . import OTTDEnums
from .OTTDClient import OTTDClient, MaxReconnectsException


class OTTDBot(OTTDClient):
    logger: logging.Logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    def __init__(self, host: str, port: int, *, command_prefix: str = "!", 
                 reconnect_delay_s: float = 5.0, max_reconnects: int = -1, logger: Optional[logging.Logger] = None ):
        
        if logger is not None:
            self.logger = logger

        super().__init__(host, port, reconnect_delay_s=reconnect_delay_s, max_reconnects=max_reconnects, logger=self.logger)

        self.command_prefix = command_prefix
        
        self.commands = {}
        self.packet_handlers: Dict[str, List[callable]] = { "PacketAdminChat": [self.default_chat_handler] }
        self.bot_tick_callbacks: List[callable] = []

    
    def default_chat_handler(self, chat_packet):
        message = chat_packet.message.decode('utf-8')
        if not message.startswith(self.command_prefix) or not len(message) > 1:
            return
        
        message = message[1:].split()
        command = message[0]
        args = message[1:]

        fro = chat_packet.fro

        cmds = self.commands.get(command)
        if cmds is None:
            self.chat_client(fro, f"Invalid command {command}")
            return

        for cmd in cmds["handlers"]:
            cmd(command, args, fro)
    

    # command decorator
    def chat_command(self, command: str = None, help: str = None):
        def decorator(command_handler):
            cmd = command or command_handler.__name__

            if cmd in self.commands:
                self.commands[cmd]["handlers"].append(command_handler)
            else:
                self.commands[cmd] = {'handlers': [command_handler], 'help': help }

            return command_handler
        return decorator
    

    def get_help_messages(self):
        helps = []
        for cmd in self.commands:
            help_msg = self.commands[cmd].get('help')
            helps.append(f'{"!"+cmd:>10} ---> {help_msg}')
        
        return helps
    

    # packet_handler decorator
    def packet_handler(self, packet_type: OTTDEnums.AdminUpdateType):
        def decorator(packet_handler):
            if packet_type in self.packet_handlers:
                self.packet_handlers[packet_type].append(packet_handler)
            else:
                self.packet_handlers[packet_type] = [packet_handler]
            
            return packet_handler
        return decorator
    

    # bot_tick decorator
    def bot_tick(self):
        def decorator(tick_handler):
            self.bot_tick_callbacks.append(tick_handler)
            return tick_handler
        return decorator
    

    def run(self):
        sleeptime_s = 1

        runtime = time.time()
        ping_interval_s = 90

        while(True):
            try:
                for tick_callback in self.bot_tick_callbacks:
                    tick_callback()

                time.sleep(sleeptime_s)

                if (time.time() - runtime) >= ping_interval_s:
                    runtime = time.time()
                    if not self.ping():
                        continue

                packet = self.receive()
                if packet is None:
                    continue

                # dispatch packet handlers
                packet_class = packet.__class__.__name__
                handlers = self.packet_handlers.get(packet_class) or self.packet_handlers.get("unhandled")
                if not handlers:
                    continue

                for handler in handlers:
                    handler(packet)
                    
            except MaxReconnectsException:
                print("Failed to reconnect to server.")
                break
            except KeyboardInterrupt:
                break

