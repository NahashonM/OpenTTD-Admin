
import math
import tabulate

from discordAdmin import run_discord_async_function
from util import cmd_processor, ctypes_values_list
from ottd_util import ConvertDateToYMD

import globals


'''
=================================================
'''
async def on_discord_admin_message(message ):

	cmd_args = cmd_processor( message.content )
	if not cmd_args or cmd_args[0] == '':			# not a valid command. treat as a message
		globals.ottdPollAdmin.chat_external('discord', str(message.author), str(message.content))
		return
	
	command = cmd_args[0]
	res = None

	match command:
		case "companies":
			res = globals.ottdPollAdmin.poll_company_info()
			header = [x[0] for x in res[0]._fields_]
			rows =  [ ctypes_values_list(x) for x in res]
			await globals.discord_bot.send_message_to_admin_channel( tabulate(rows, header) )
		
		case "clients":
			res = globals.ottdPollAdmin.poll_client_info()
			header = [x[0] for x in res[0]._fields_]
			rows =  [ ctypes_values_list(x) for x in res]
			await globals.discord_bot.send_message_to_admin_channel( tabulate(rows, header) )

		case "date":
			res = globals.ottdPollAdmin.poll_current_date()
			await globals.discord_bot.send_message_to_admin_channel( ConvertDateToYMD(res.ticks ) )
		
		case "rcon":
			rcommand = ' '.join(cmd_args[1:])
			rcon_res, _ = globals.ottdPollAdmin.rcon_cmd(rcommand)

			res = ''
			for rc_res in rcon_res:
				res += rc_res.text.decode() + '\n'


			await globals.discord_bot.send_message_to_admin_channel( res )



def on_discord_message(message):
	globals.ottdPollAdmin.chat_external('discord', str(message.author), str(message.content))
	# print(f"ingme Message from {message.author}: {message.content} channel: {message.channel}")

