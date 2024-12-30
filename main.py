import os
import time
import logging
import threading
import discord
import signal
import argparse

from dotenv import load_dotenv
load_dotenv()

from openttd.ottd import OpenTTD
from discord.bot import DiscordBot

import discord_handlers as discord_handlers

import ottd_handlers
import openttd.ottd_enum as ottdenum

import globals


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger( os.path.basename(__file__))


def parse_cmd_arguments():
    parser = argparse.ArgumentParser(
                    prog = os.path.basename(__file__),
                    description = 'OpenTTD Admin client',
                    epilog = 'To report any bugs reach out to the dev via')
    
    parser.add_argument('-e', '--env',
                        action='store_true', 
                        help="Generate .env file and exit.")

    return parser.parse_args()



# gen_env_file
# 
# regenerate .env file
#---------------------------------------------------
def gen_env_file():
	env_path = os.path.join( os.path.dirname(os.path.realpath(__file__)) , '.env' )
	with open(env_path, 'w') as env_file:
		env_file.write(
'''
#	Discord Configs
#-----------------------------------------
DISCORD_TOKEN = _your_discord_bot_token_
DISCORD_GUILD = _your_discord_server_
DISCORD_ADMIN_CHANNEL = _your_discord_channel_to_send_admin_messages_
DISCORD_INGAME_CHANNEL = _your_discord_channel_to_send_ingame_chat_messages_
DISCORD_DELETE_MSGS_AFTER = _how_long_in_secons_to_keep_messages_
DISCORD_CMD_PREFIX = !

#	OpenTTD Server Configs
#-----------------------------------------
OPENTTD_HOST = _openttd_server_ip_or_hostname_
OPENTTD_ADMIN_PORT = _openttd_server_admin_port_
OPENTTD_ADMIN_NAME = _openttd_admin_name_for_polling_services_
OPENTTD_ADMIN_PASSWORD = _openttd_admin_password_
''')
	
	print(f'.env file generated in {env_path}')
      


def init_discord_bot():
    #---- Parse Env Args ----
    discord_token = os.getenv("DISCORD_TOKEN")
    discord_guild = os.getenv("DISCORD_GUILD")  # servers   
    admin_channel_name = os.getenv("DISCORD_ADMIN_CHANNEL")
    ingame_channel_name = os.getenv("DISCORD_INGAME_CHANNEL")
    command_prefix = os.getenv("DISCORD_CMD_PREFIX")

    globals.msg_delete_timeout = os.getenv("DISCORD_DELETE_MSGS_AFTER")

    #---- Init Bot ----
    intents = discord.Intents.default()
    intents = discord.Intents.all()
    intents.message_content = True

    discordBot = DiscordBot(discord_guild, admin_channel_name, ingame_channel_name, intents=intents, command_prefix=command_prefix)
	
    discord_handlers.register_discord_bot_commands(discordBot)

    discordBot.register_on_admin_message_callback( discord_handlers.on_discord_admin_message )
    discordBot.register_on_ingame_message_callback( discord_handlers.on_discord_message )

    discord_thread = threading.Thread(target = discordBot.run, args = (discord_token, ))
    discord_thread.start()

    return discordBot, discord_thread



def init_openttd_admin():
    #---- Parse Env Args ----
    openttd_host = os.getenv("OPENTTD_HOST")
    openttd_admin_port = os.getenv("OPENTTD_ADMIN_PORT")
    openttd_admin_user = os.getenv("OPENTTD_ADMIN_NAME")
    openttd_admin_paswd = os.getenv("OPENTTD_ADMIN_PASSWORD")

    openttd = OpenTTD(openttd_host, openttd_admin_port)

    #---- Register packet Handlers ----
    for handler in ottd_handlers.OTTD_AUTO_UPDATE_HANDLERS:
        openttd.register_pkt_handler(handler, ottd_handlers.OTTD_AUTO_UPDATE_HANDLERS[handler])

    
    #---- Join Server ----
    openttd.join_server(openttd_admin_user, openttd_admin_paswd)

    openttd.set_is_ready(True)

    return openttd
     



#------------------ Main --------------------------
#---------------------------------------------------
if __name__ == "__main__":
    args = parse_cmd_arguments()
    
    if args.env:
        gen_env_file()
        exit(0)
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    #------- init openttd server
    try:
        globals.openttd = init_openttd_admin()

        globals.openttd.request_auto_update_company_info()
        globals.openttd.request_auto_update_client_info()
        globals.openttd.request_auto_update_chat()
        globals.openttd.request_auto_update_date(ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_QUARTERLY)

    except:
        logger.error('Error initializing openttd admin.')
        exit(0)
    
    
    #------- init discord bot  
    try:
        # globals.discord_bot, globals.discord_thread = init_discord_bot()
        pass
    except:
        logger.error('Error initializing discord admin.')
        exit(0)
    
    
    #------- start discord admin
    # globals.discord_bot.staart()

    
    #------- start openttd admin
    globals.openttd.run()
    
    # -- end
    globals.discord_thread.join()




logger.warning("This file is not intended to be a module but a main application")