import os
import math 
import re
import logging
import json

from discord.bot import run_discord_async_function
from util import cmd_processor
from openttd.ottd_util import ConvertDateToYMD


import openttd.ottd_enum as ottdenum
import globals

logger = logging.getLogger( os.path.basename(__file__))

rules_menu = [
	'========================== Rules =====================================',
	'1. Please respect fellow players.',
	'2. Do not block other companies.',
	'3. Except for cities, Do not build station(s) on factories already being served by another company.',
	'     Rule 3 is void only if you have permission from second company.',
	'4. Do not intentionally destroy other companies vehicles with trains.',
	'======================================================================='
]


help_menu = [
	'==================== Help ==========================',
	'!help : View this help message.',
	'!rules : View house rules.',
	'!reset : Wipe current company. (you must be the only player in the company.)',
	'!admin : Request for admin help.',
	'  '
	'********* Please note *********',
	' a) all commands have the format !_command_ .',
	' b) all commands are in the public chat.',
	'===================================================='
]


def log_console_and_discord(message):	
	logger.info(message)
	run_discord_async_function(globals.discord_bot.send_message_to_ingame_channel(f">> {message}"))


def escape_user_name(username):
	return re.sub('([\*\_~])', r'\\\1', username)


def no_handler(_):
	pass


'''
==================================================================
'''
def ottd_PacketAdminChat_handler( chat ):
	message = chat.message.decode()
	if not message or message == '':				# empty message with no body
		return

	cmd_args = cmd_processor( message )

	if not cmd_args or cmd_args[0] == '':			# not a valid command. treat as a message
		if chat.dest_type == ottdenum.DestType.DESTTYPE_BROADCAST:
			player_name = ''
			try: player_name = f'[#{chat.to}] {globals.ottd_clients[chat.to]["name"]} '
			except: player_name = f'[#{chat.to}] '

			run_discord_async_function( 
				globals.discord_bot.send_message_to_ingame_channel( f"*{escape_user_name(player_name)}*: {message}") )
		return
	

	match cmd_args[0]:
		case "help":
			for help_msg in help_menu:
				globals.openttd.chat_client(chat.to, help_msg)
			return
		
		case "rules":
			for rule_msg in rules_menu:
				globals.openttd.chat_client(chat.to, rule_msg)
			return
		
		case "reset":
			company = ottdenum.MAX_UBYTE
			try: company = globals.ottd_clients[chat.to]['company']
			except: pass

			# Cannor reset default specator company
			if company == ottdenum.MAX_UBYTE:
				globals.openttd.chat_client(chat.to, "Failed. You need to be in a company to reset it.")
				return
			
			# cannot reset company if multiple users are in it
			count = 0
			for player_id in globals.ottd_clients:
				player = globals.ottd_clients[player_id]
				try: 
					if player['company'] == company: 
						count += 1
				except: pass

				if count > 1: 
					globals.openttd.chat_client(chat.to, "Failed. There are other players in the company.")
					globals.openttd.chat_client(chat.to, "  If you need an admins help, type !admin")

					return

			# move player to spectators
			globals.openttd.rcon_cmd(f'move {chat.to} {ottdenum.MAX_UBYTE}')

			# reset company
			globals.openttd.rcon_cmd(f'reset_company {company + 1}')

			return
		
		case "admin":
			message = '' 
			if len(cmd_args) > 1:
				message = ' '.join(cmd_args[1:])
			else:
				message = 'help'
			
			player_name = ''
			try: player_name = f'(#{chat.to}):{globals.ottd_clients[chat.to]["name"]}'
			except: player_name = f'(#{chat.to})'

			run_discord_async_function(globals.discord_bot.send_message_to_admin_channel( f"Admin call\nfrom: {player_name}\nmsg: {message} "  ))
			return


'''
	ottd_ClientJoin_handler

	handler for events raised when:
		1. a player joins the server
	==================================================================
'''
def ottd_ClientJoin_handler( client ):

	# out of sync (OOS) with server
	# poll for clients and leave
	if client.id not in globals.ottd_clients:
		globals.ottd_clients.clear()
		globals.openttd.poll_client_info()
		return
	
	# send welcome to player
	name = globals.ottd_clients[client.id]['name']

	#run_discord_async_function( 
	#	globals.discord_bot.send_message_to_ingame_channel(f'(#{client.id}):{client.name.decode()} has joined the game') )
	
	globals.openttd.chat_client(client.id,f'====================================================')
	globals.openttd.chat_client(client.id,f'Hello {name}')
	globals.openttd.chat_client(client.id,f'Welcome to {globals.serverWelcome.name.decode()}.')
	globals.openttd.chat_client(client.id,f'Please respect fellow players')
	globals.openttd.chat_client(client.id,f'====================================================')
	globals.openttd.chat_client(client.id,f'Type !help for commands help')
	globals.openttd.chat_client(client.id,f'Type !rules to view house rules')
	globals.openttd.chat_client(client.id,f'====================================================')




'''
	ottd_ClientInfo_handler

	handler for events raised when:
		1. a player joins the server
		2. admin polls for client info
	================================================================================
'''
def ottd_ClientInfo_handler( client ):

	globals.ottd_clients[client.id] = {
			'name': client.name.decode(),
			'ip': client.ip,
			'language': client.language,
			'join_date': client.join_date,
			'company': client.company,
		}



'''
	ottd_ClientUpdate_handler

	handler for events raised when:
		1. a player changes teams
		2. a player changes their username
	==================================================================
'''
def ottd_ClientUpdate_handler( client ):

	# out of sync (OOS) with server
	# poll for clients and leave
	if client.id not in globals.ottd_clients:
		globals.ottd_clients.clear()
		globals.openttd.poll_client_info()
		return

	
	# team change
	if client.playas != globals.ottd_clients[client.id]['company']:
		globals.ottd_clients[client.id]['company'] = client.playas

		# check if not founding company or joining spectators
		if client.playas in globals.ottd_companies or client.playas == ottdenum.MAX_UBYTE:
			company_name = 'spectators'
			info_text = 'has joined'

			if client.playas != ottdenum.MAX_UBYTE:
				company_name = globals.ottd_companies[client.playas]['name']
				info_text += ' company'
			
			log_console_and_discord( f"{globals.ottd_clients[client.id]['name']} {info_text} {company_name}" )

		return
	
	# name change
	if client.name.decode() != globals.ottd_clients[client.id]['name']:
		old_name = globals.ottd_clients[client.id]['name']
		globals.ottd_clients[client.id]['name'] = client.name.decode()

		log_console_and_discord( f"{old_name} changed their name to {client.name.decode()}" )

		return
	
	logger.warn("An unidentified player update was received")
	logger.warn(f"   old player id:{client.id} name:{globals.ottd_clients[client.id]['name']} company:{globals.ottd_clients[client.id]['company']}")
	logger.warn(f"   new player id:{client.id} name:{client.name.decode()} company:{client.playas}")
	
	return




'''
	ottd_ClientQuit_handler

	handler for events raised when:
		1. a player leaves the game
==================================================================
'''
def ottd_ClientQuit_handler( client ):

	# out of sync (OOS) with server
	# poll for clients and leave
	if client.id not in globals.ottd_clients:
		globals.ottd_clients.clear()
		globals.openttd.poll_client_info()
		return

	client_name = globals.ottd_clients[client.id]['name']

	del globals.ottd_clients[client.id]

	log_console_and_discord(f"{client_name} has left the game")



'''
	ottd_CompanyNew_handler

	handler for events raised when:
		1. a new company is created
	==================================================================
'''
def ottd_CompanyNew_handler( company ):

	# out of sync (OOS) with server
	# poll for companies and leave
	if company.id not in globals.ottd_companies:
		globals.ottd_companies.clear()
		globals.openttd.poll_company_info()
		return
	
	# send notification to discord
	team = company.id + 1
	founder_id = 0
	
	for player in globals.ottd_clients:
		if globals.ottd_clients[player]['company'] == company.id:
			founder_id = player
			break
		
	globals.openttd.chat_team(team, "====================================================")
	globals.openttd.chat_team(team, "x  Remember to secure the company with a password  x")
	globals.openttd.chat_team(team, "x        unprotected companies will be reset       x")
	globals.openttd.chat_team(team, "====================================================")
	
	log_console_and_discord(f'{ globals.ottd_clients[founder_id]["name"] } started new company {globals.ottd_companies[company.id]["name"]}')



'''
	ottd_CompanyInfo_handler

	handler for events raised when:
		1. new company is created
		2. admin polls for company info
	==================================================================
'''
def ottd_CompanyInfo_handler( company ):
	globals.ottd_companies[company.id] = {
			'name': company.name.decode(),
			'president': company.president.decode(),
			'color': company.color,
			'is_protected': company.is_protected,
			'start_date': company.start_date,
			'quaters_bankrupt': company.quaters_bankrupt,
			'share_owners': company.share_owners,
		}



'''
	ottd_CompanyUpdate_handler

	handler for events raised when:
		1. company name changes
		2. company president changes
		3. company bankruptcy state change
		4. company changes color
		5. company is passworded
		6. company gets new share owners
	==================================================================
'''
def ottd_CompanyUpdate_handler( company ):
	
	# out of sync (OOS) with server
	# poll for companies and leave
	if company.id not in globals.ottd_companies:
		globals.ottd_companies.clear()
		globals.openttd.poll_company_info()
		return
	
	old_state = globals.ottd_companies[company.id]

	globals.ottd_companies[company.id] = {
			'name': company.name.decode(),
			'president': company.president.decode(),
			'color': company.color,
			'is_protected': company.is_protected,
			'quaters_bankrupt': company.quaters_bankrupt,
			'share_owners': company.share_owners,
		}

	

	# company name change
	if old_state["name"] != globals.ottd_companies[company.id]["name"]:
		log_console_and_discord(f"{old_state['name']} is now {globals.ottd_companies[company.id]['name']}")

	# is passworded
	elif old_state["is_protected"] != company.is_protected:
		if company.is_protected:
			log_console_and_discord(f"{old_state['name']} is now locked")
		else:
			log_console_and_discord(f"{old_state['name']} is now unlocked")

	# others
	# TODO --- handle or ignore

	

	return


'''
	ottd_CompanyRemove_handler

	handler for events raised when:
		1. company is deleted
	==================================================================
'''
def ottd_CompanyRemove_handler( company ):
	
	# out of sync (OOS) with server
	# poll for clients and leave
	if company.id not in globals.ottd_companies:
		globals.ottd_companies.clear()
		globals.openttd.poll_company_info()
		return

	company_name = globals.ottd_companies[company.id]['name']

	del globals.ottd_companies[company.id]

	log_console_and_discord(f"{company_name} has been closed down and assets sold")



'''
==================================================================
'''
def ottd_ServerDate_handler( date ):
	pass


'''
	ottd_ServerNewGame_handler

	handler for events raised when:
		1. the server restarts a new game
==================================================================
'''
def ottd_ServerNewGame_handler( _ ):
	# clear all clients
	globals.ottd_clients.clear()

	# clear all companies
	globals.ottd_companies.clear()

	# alert new game is starting
	log_console_and_discord('**--------- New Game Started ---------**')


'''
	ottd_ServerWelcome_handler

	handler for events raised when:
		1. admin joins a new server
		2. the admin rejoins a server after restart
==================================================================
'''
def ottd_ServerWelcome_handler( packet ):
	logger.info(f' Welcome to server {packet.name}')

	globals.serverWelcome  = packet

	# force client info to be sent
	globals.ottd_clients.clear()
	globals.openttd.poll_client_info()

	# force company info to be sent
	globals.ottd_companies.clear()
	globals.openttd.poll_company_info()


'''
	ottd_ClientError_handler

	handler for events raised when:
		1. admin client makes an error
==================================================================
'''
def ottd_ClientError_handler( _ ):
	logger.error('Client made an error')


OTTD_AUTO_UPDATE_HANDLERS = {
		'PacketAdminChat'	: ottd_PacketAdminChat_handler,
		'ClientJoin'		: ottd_ClientJoin_handler,
		'ClientInfo'		: ottd_ClientInfo_handler,
		'ClientUpdate'		: ottd_ClientUpdate_handler,
		'ClientQuit'		: ottd_ClientQuit_handler,
		'ClientError'		: ottd_ClientError_handler,
		'CompanyNew'		: ottd_CompanyNew_handler,
		'CompanyInfo'		: ottd_CompanyInfo_handler,
		'CompanyEconomy'	: no_handler,
		'CompanyStats'		: no_handler,
		'CompanyUpdate'		: ottd_CompanyUpdate_handler,
		'CompanyRemove'		: ottd_CompanyRemove_handler,
		'ServerDate'		: ottd_ServerDate_handler,
		'ServerNewGame'		: ottd_ServerNewGame_handler,
		'ServerWelcome'		: ottd_ServerWelcome_handler,
}