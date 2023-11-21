
import math
import tabulate


from discordAdmin import run_discord_async_function
from util import cmd_processor, ctypes_values_list
from ottd_util import ConvertDateToYMD

import ottd_enum as ottdenum
import globals


def register_discord_bot_commands( bot ):
	@bot.command()
	async def companies(ctx):
		res = globals.ottdPollAdmin.poll_company_info()
		header = [x[0] for x in res[0]._fields_]
		rows =  [ ctypes_values_list(x) for x in res]

		await ctx.channel.send( tabulate(rows, header) )


	@bot.command()
	async def clients(ctx):
		res = globals.ottdPollAdmin.poll_client_info()
		header = [x[0] for x in res[0]._fields_]
		rows =  [ ctypes_values_list(x) for x in res]

		await ctx.channel.send( tabulate(rows, header) )
	
	
	@bot.command()
	async def date(ctx):
		res = globals.ottdPollAdmin.poll_current_date()

		await ctx.channel.send(  ConvertDateToYMD(res.ticks )  )


	@bot.command()
	async def rcon(ctx, *, command):
		try:
			rcon_res, _ = globals.ottdPollAdmin.rcon_cmd(command)

			res = ''
			for rc_res in rcon_res:
				res += rc_res.text.decode() + '\n'

			await ctx.channel.send( res )
		except:
			await ctx.channel.send( "something is not right" )

	

	@bot.command()
	async def clean(ctx, channel_name, count):
		try:
			count = int(count)

			for channel in ctx.channel.guild.channels:
				if channel.name == channel_name:
					messages = [message async for message in channel.history(limit=count)]
					begin = 0
					end = count
					if count > 100: end = 100

					while end < count:
						await channel.delete_messages(messages[begin:end] )
						begin = end
						remaining = count - end
						
						if remaining < 0: break

						if remaining > 100: end += 100
						else: end += remaining
						

					await ctx.channel.send( f"Deleted {count} messages from {channel_name}" )
					return
			
			await ctx.channel.send( "Channel not managed by bot" )
			
		except Exception as e:
			print(e)
			await ctx.channel.send( "somethings not right" )
		




'''
=================================================
'''
def on_discord_admin_message(message ):
	globals.ottdPollAdmin.chat_external('discord','admin', str(message.content), ottdenum.TextColor.TC_RED )
	


def on_discord_message(message):
	globals.ottdPollAdmin.chat_external('discord', str(message.author), str(message.content))


