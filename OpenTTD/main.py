'''

'''
import os
import time
import logging
import threading
import discord
import signal
import argparse

from dotenv import load_dotenv
load_dotenv()


from ottd_poll import OttdPoll
from ottd_update import OttdUpdate
from discordAdmin import DiscordBot

import ottd_enum as ottdenum

import discord_msg_handlers
import ottd_update_handlers

import globals


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")


def parse_cmd_arguments():
    parser = argparse.ArgumentParser(
                    prog = os.path.basename(__file__),
                    description = 'OpenTTD Admin client',
                    epilog = 'To report any bugs reach out to the dev via')
    
    parser.add_argument('-e', '--env',
                        action='store_true', 
                        help="Generate .env file and exit.")

    return parser.parse_args()


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

#	OpenTTD Server Configs
#-----------------------------------------
OPENTTD_HOST = _openttd_server_ip_or_hostname_
OPENTTD_ADMIN_PORT = _openttd_server_admin_port_
OPENTTD_ADMIN_NAME_1 = _openttd_admin_name_for_polling_services_
OPENTTD_ADMIN_NAME_2 = _openttd_admin_name_for_auto_update_services_
OPENTTD_ADMIN_PASSWORD = _openttd_admin_password_
''')
	
	print(f'.env file generated in {env_path}')


'''
	Start discord bot
'''
def init_discord_bot():

	intents = discord.Intents.default()
	intents.message_content = True

	bot = DiscordBot(discord_guild, admin_channel_name, ingame_channel_name, intents=intents)

	bot.register_on_admin_message_callback( discord_msg_handlers.on_discord_admin_message )
	bot.register_on_ingame_message_callback( discord_msg_handlers.on_discord_message )

	discord_thread = threading.Thread(target = bot.run, args=(discord_token, ))
	discord_thread.start()

	return bot, discord_thread



'''
	Main OpenTTD update thread

	Listens for all OpenTTD update events that were registered during startup
'''
def start_ottd_update_watcher():

	while True:
		time.sleep(0.1)
		update = globals.ottdUpdateAdmin.get_update()

		if not update:
			continue

		if type(update) == list:
			for entry in update:
				print("\t ", entry )
			
			return
		
		try:
			ottd_update_handlers.OTTD_AUTO_UPDATE_HANDLERS[type(update).__name__](update)
		except:
			pass
		


if __name__ == "__main__":
	args = parse_cmd_arguments()
	

	if args.env:
		gen_env_file()
		exit(0)


	signal.signal(signal.SIGINT, signal.SIG_DFL)

	'''
	---------- Discord Env -------------
	'''
	discord_token = os.getenv("DISCORD_TOKEN")
	discord_guild = os.getenv("DISCORD_GUILD")  # servers

	admin_channel_name = os.getenv("DISCORD_ADMIN_CHANNEL")
	ingame_channel_name = os.getenv("DISCORD_INGAME_CHANNEL")

	'''
	---------- OpenTTD Server Env -------------
	'''
	openttd_host = os.getenv("OPENTTD_HOST")
	openttd_admin_port = os.getenv("OPENTTD_ADMIN_PORT")
	openttd_admin_user1 = os.getenv("OPENTTD_ADMIN_NAME_1")
	openttd_admin_user2 = os.getenv("OPENTTD_ADMIN_NAME_2")
	openttd_admin_paswd = os.getenv("OPENTTD_ADMIN_PASSWORD")



	# start discord bot thread
	#---------------------------------
	globals.discord_bot, discord_thread = init_discord_bot()


	# Connected to game server
	#---------------------------------
	globals.ottdPollAdmin = OttdPoll(openttd_host, openttd_admin_port)
	globals.ottdUpdateAdmin = OttdUpdate(openttd_host, openttd_admin_port)
	
	serv_protocol, server_welcome = globals.ottdPollAdmin.join_server( openttd_admin_user1, openttd_admin_paswd )
	if not serv_protocol or not server_welcome:
		logger.error("Could not connect to server. Please verify credentials")
		exit(-1)
	
	globals.serverWelcome = server_welcome

	serv_protocol, server_welcome = globals.ottdUpdateAdmin.join_server( openttd_admin_user2, openttd_admin_paswd ) 
	if not serv_protocol or not server_welcome:
		logger.error("Could not connect to server. Please verify credentials")
		exit(-1)

	
	# register openttd updates
	#-------------------------------------
	globals.ottdUpdateAdmin.request_date_updates( ottdenum.AdminUpdateFrequency.ADMIN_FREQUENCY_QUARTERLY )
	globals.ottdUpdateAdmin.request_chat_updates()
	globals.ottdUpdateAdmin.request_client_info_updates()
	globals.ottdUpdateAdmin.request_company_info_updates()
	# globals.ottdUpdateAdmin.request_company_stats_updates()


	# populate ottd_clients dict
	#-------------------------------------
	res = globals.ottdPollAdmin.poll_client_info()

	for client in res:
		globals.ottd_clients[client.id] = {
			'name': client.name.decode(),
			'join_date': client.join_date,
			'company': client.company,
			'new': False,
		}


	# start consuming openttd updates
	#---------------------------------
	ottd_update_thread = threading.Thread(target= start_ottd_update_watcher )
	ottd_update_thread.start()


	# TODO watch if any of the threads is dead
	#-------------------------------------


	ottd_update_thread.join()
	discord_thread.join()


	exit(0)


logger.warning("This file is not intended to be a module but a main application")