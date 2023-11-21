
import math 
import logging

from discordAdmin import run_discord_async_function
from util import cmd_processor
from ottd_util import ConvertDateToYMD


import ottd_enum as ottdenum
import globals

logger = logging.getLogger("ottd_update_handler")

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
			run_discord_async_function( globals.discord_bot.send_message_to_ingame_channel( message ) )
		return
	

	match cmd_args[0]:
		case "help":
			for help_msg in help_menu:
				globals.ottdPollAdmin.chat_client(chat.to, help_msg)
			return
		
		case "rules":
			for rule_msg in rules_menu:
				globals.ottdPollAdmin.chat_client(chat.to, rule_msg)
			return
		
		case "reset":
			company = ottdenum.MAX_UBYTE
			try: company = globals.ottd_clients[chat.to]['company']
			except: pass

			if company == ottdenum.MAX_UBYTE:
				globals.ottdPollAdmin.chat_client(chat.to, "Failed. You need to be in a company to reset it.")
				return
			

			count = 0
			for player_id in globals.ottd_clients:
				player = globals.ottd_clients[player_id]
				try: 
					if player['company'] == company: 
						count += 1
				except: pass

				if count > 1: 
					globals.ottdPollAdmin.chat_client(chat.to, "Failed. There are other players in the company.")
					globals.ottdPollAdmin.chat_client(chat.to, "  If you need an admins help, type !admin")

					return

			globals.ottdPollAdmin.rcon_cmd(f'move {chat.to} {ottdenum.MAX_UBYTE}')
			globals.ottdPollAdmin.rcon_cmd(f'reset_company {company + 1}')
			globals.ottdPollAdmin.poll_company_remove_reason()

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

			run_discord_async_function( 
				globals.discord_bot.send_message_to_admin_channel( f"Admin call\nfrom: {player_name}\nmsg: {message} "  ))
			return


'''
==================================================================
'''
def ottd_ClientJoin_handler( client ):
	if client.id in globals.ottd_clients:
		return

	globals.ottd_clients[client.id] = {
			'name': None,
			'join_date': client.join_date,
			'company': client.company,
			'new': True,
		}



'''
	ottd_ClientInfo_handler

	handler for events raised when:
		a player joins a game and their infor is sent to the server
	
	The event is raised automatically only once.
	subsequent requests are via poll commands
	================================================================================
'''
def ottd_ClientInfo_handler( client ):
	if client.id in globals.ottd_clients and globals.ottd_clients[client.id].new != True:
		return

	globals.ottd_clients[client.id] = {
			'name': client.name.decode(),
			'join_date': client.join_date,
			'company': client.company,
			'new': False,
		}
	
	run_discord_async_function( 
		globals.discord_bot.send_message_to_ingame_channel(f'(#{client.id}):{client.name.decode()} has joined the game') )
	
	globals.ottdPollAdmin.chat_client(client.id,f'====================================================')
	globals.ottdPollAdmin.chat_client(client.id,f'Hello {client.name.decode()}')
	globals.ottdPollAdmin.chat_client(client.id,f'Welcome to {globals.serverWelcome.name.decode()}.')
	globals.ottdPollAdmin.chat_client(client.id,f'Please respect fellow players')
	globals.ottdPollAdmin.chat_client(client.id,f'====================================================')
	globals.ottdPollAdmin.chat_client(client.id,f'Type !help for commands help')
	globals.ottdPollAdmin.chat_client(client.id,f'Type !rules to view house rules')
	globals.ottdPollAdmin.chat_client(client.id,f'====================================================')


'''
	ottd_ClientUpdate_handler

	handler for events raised when:
		a player changes teams
		a player changes their username
==================================================================
'''
def ottd_ClientUpdate_handler( client ):	
	if client.id not in globals.ottd_clients:
		logger.error('ClientUpdate:', 'Received updated from client not in global client list')
		
	try:
		if client.playas != globals.ottd_clients[client.id]['company']:
			new_company = ''

			if client.playas == ottdenum.MAX_UBYTE:		# has joined spectators
				new_company = 'spectators'
			else:
				company_info = globals.ottdPollAdmin.poll_company_info( client.playas )
				if company_info: new_company = f'(#{company_info.id}):{company_info.name.decode()}'
			
			run_discord_async_function( 
				globals.discord_bot.send_message_to_ingame_channel(
					f'(#{client.id}):{client.name.decode()} has joined {new_company}') )
			
			globals.ottd_clients[client.id]['company'] = client.playas
			return

		elif client.name.decode() != globals.ottd_clients[client.id]['name']:
			run_discord_async_function( 
				globals.discord_bot.send_message_to_ingame_channel(
					f'(#{client.id}):{client.name.decode()} has changed their name to {client.name.decode()}') )
			
			globals.ottd_clients[client.id]['name'] = client.name.decode()

			
	except Exception as e:
		logger.error('ClientUpdate:', e)



'''
	ottd_ClientQuit_handler

	handler for events raised when:
		a player leaves the game
==================================================================
'''
def ottd_ClientQuit_handler( client ):

	client_name = ''

	if client.id in globals.ottd_clients:
		try:
			client_name = globals.ottd_clients[client.id]['name']
		except Exception as e:
			logger.error('ClientQuit:', e)

		del globals.ottd_clients[client.id]
	
	run_discord_async_function( 
		globals.discord_bot.send_message_to_ingame_channel(f'(#{client.id}):{client_name} has left the game' ) )

	


'''
==================================================================
'''
def ottd_CompanyNew_handler( company ):
	try:
		company_info = globals.ottdPollAdmin.poll_company_info( company.id )
		clients = globals.ottdPollAdmin.poll_client_info()

		founding_client = None

		for client in clients:
			if client.company == company.id:
				founding_client = client

		run_discord_async_function( 
			globals.discord_bot.send_message_to_ingame_channel(
				f'(#{founding_client.id}):{founding_client.name.decode()} started new company (#{company_info.id}):{company_info.name}') )
			
		globals.ottdPollAdmin.chat_team(company.id + 1, "====================================================")
		globals.ottdPollAdmin.chat_team(company.id + 1, "x  Remember to secure the company with a password  x")
		globals.ottdPollAdmin.chat_team(company.id + 1, "x        unprotected companies will be reset       x")
		globals.ottdPollAdmin.chat_team(company.id + 1, "====================================================")


	except Exception as e:
		logger.error('CompanyNew', e)


'''
==================================================================
'''
def ottd_CompanyUpdate_handler( company ):
	print( 'company update', company)


'''
==================================================================
'''
def ottd_CompanyRemove_handler( company ):
	print( 'company remove', company)


'''
==================================================================
'''
def ottd_ServerDate_handler( date ):
	parsed_date =  ConvertDateToYMD( date.ticks )
	new_quarter = math.floor(parsed_date[1] / 3) + 1
	if new_quarter < 5:
		run_discord_async_function( globals.discord_bot.send_message_to_ingame_channel(f'Quarter Q{new_quarter} for the year {parsed_date[0]} begins.' ) )



OTTD_AUTO_UPDATE_HANDLERS = {
		'PacketAdminChat'	: ottd_PacketAdminChat_handler,
		'ClientJoin'		: ottd_ClientJoin_handler,
		'ClientInfo'		: ottd_ClientInfo_handler,
		'ClientUpdate'		: ottd_ClientUpdate_handler,
		'ClientQuit'		: ottd_ClientQuit_handler,
		'CompanyNew'		: ottd_CompanyNew_handler,
		'CompanyInfo'		: no_handler,
		'CompanyEconomy'	: no_handler,
		'CompanyStats'		: no_handler,
		'CompanyUpdate'		: ottd_CompanyUpdate_handler,
		'CompanyRemove'		: ottd_CompanyRemove_handler,
		'ServerDate'		: ottd_ServerDate_handler,
}