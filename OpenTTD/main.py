'''

'''
import os
import time
import logging
import threading
import argparse
import discord
import signal


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


discord_token = os.getenv("DISCORD_TOKEN")
discord_guild = os.getenv("DISCORD_GUILD")  # servers

admin_channel_name = os.getenv("DISCORD_ADMIN_CHANNEL")
ingame_channel_name = os.getenv("DISCORD_INGAME_CHANNEL")


def parse_cmd_arguments():
    parser = argparse.ArgumentParser(
                    prog = os.path.basename(__file__),
                    description = 'OpenTTD Admin client',
                    epilog = 'To report any bugs reach out to the dev via email: nahashonm386@gmail.com.')
    
    parser.add_argument('-s', '--server', type=str,
                        metavar='ip:admin-port',
                        default="127.0.0.1:3977", 
                        help="Game server ip and port. Default=127.0.0.1:3977")
    
    parser.add_argument('-r', '--rabbitmq', type=str,
                        metavar='ip:port',
                        default="127.0.0.1:5672", 
                        help="RabbitMQ server ip and port. Default=127.0.0.1:5672")
    
    parser.add_argument('-u', '--user', type=str,
                        metavar='name',
                        default="admin", 
                        help="text to use as username when connecting to OpenTTD admin port. Default=admin")
    
    parser.add_argument('-p', '--pswd', type=str,
                        metavar='pswd', 
                        default="!@Admin123", 
                        help="Password configured for the admin port in OpenTTD. Default is empty password")

    return parser.parse_args()





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

	signal.signal(signal.SIGINT, signal.SIG_DFL)

	ottd_host, ottd_admin_port = args.server.split(':')

	# start discord bot thread
	#---------------------------------
	globals.discord_bot, discord_thread = init_discord_bot()


	# Connected to game server
	#---------------------------------
	globals.ottdPollAdmin = OttdPoll(ottd_host, ottd_admin_port)
	globals.ottdUpdateAdmin = OttdUpdate(ottd_host, ottd_admin_port)
	
	serv_protocol, server_welcome = globals.ottdPollAdmin.join_server('pollAdmin','!@Admin123')
	if not serv_protocol or not server_welcome:
		logger.error("Could not connect to server. Please verify credentials")
		exit(-1)
	
	globals.serverWelcome = server_welcome

	serv_protocol, server_welcome = globals.ottdUpdateAdmin.join_server('updateAdmin','!@Admin123') 
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


	# watch if any of the threads is dead
	#-------------------------------------


	ottd_update_thread.join()
	discord_thread.join()


	exit(0)


logger.warning("This file is not intended to be a module but a main application")