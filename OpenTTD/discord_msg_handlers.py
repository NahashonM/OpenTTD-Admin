

import os
import threading
import asyncio
import logging
from tabulate import tabulate

from discord.bot import run_discord_async_function
from util import cmd_processor, ctypes_values_list
from openttd.ottd_util import ConvertDateToYMD

import openttd.ottd_enum as ottdenum
import globals


logger = logging.getLogger( os.path.basename(__file__))


def register_discord_bot_commands( bot ):
	@bot.command()
	async def companies(ctx):
		if len(globals.ottd_companies) <= 0:
			print("server is empty")
			return
		try:
			header =  list(next(iter(globals.ottd_companies.values())).keys())
			header.insert(0, 'id')

			rows = [[client_id, *fields.values()] for client_id, fields in globals.ottd_companies.items()]

			await ctx.channel.send( tabulate(rows, header) )
		except Exception as e:
			logger.error(e)
			await ctx.channel.send( "An error occured" )
	

	@bot.command()
	async def clients(ctx):
		if len(globals.ottd_clients) <= 0:
			print("server is empty")
			return
		try:
			header =  list(next(iter(globals.ottd_clients.values())).keys())
			header.insert(0, 'id')

			rows = [[client_id, *fields.values()] for client_id, fields in globals.ottd_clients.items()]

			await ctx.channel.send( tabulate(rows, header) )
		except Exception as e:
			logger.error(e)
			await ctx.channel.send( "An error occured" )


	@bot.command()
	async def date(ctx):
		# TODO ---
		# get date from event
		pass

	# 	async def send_res(date):
	# 		await ctx.channel.send(  ConvertDateToYMD(date.ticks ) )

	# 	OpenTTDCallback("ServerDate", send_res)
	# 	res = globals.openttd.poll_current_date()

	@bot.command()
	async def ban(ctx, player_id):
		try:
			p_id = int(player_id)

			if p_id <= 0:
				await ctx.channel.send( "invalid client" )
				return
			
			globals.openttd.rcon_cmd(f'ban {p_id}')
		except:
			await ctx.channel.send( "An error occured" )


	@bot.command()
	async def kick(ctx, player_id):
		try:
			p_id = int(player_id)

			if p_id <= 0:
				await ctx.channel.send( "invalid client" )
				return
			
			globals.openttd.rcon_cmd(f'kick {p_id}')
		except:
			await ctx.channel.send( "An error occured" )


	@bot.command()
	async def mov(ctx, player_id, company_id):
		try:
			p_id = int(player_id)
			c_id = int(company_id)

			if p_id <= 0:
				await ctx.channel.send( "invalid client" )
				return

			if c_id <= 0 or c_id > 255:
				await ctx.channel.send( "invalid company" )
				return
			
			globals.openttd.rcon_cmd(f'move {p_id} {c_id}')
		except:
			await ctx.channel.send( "An error occured" )


	@bot.command()
	async def reset(ctx, company_id):
		try:
			id = int(company_id)
			if id <= 0 or id == 255:
				await ctx.channel.send( "invalid company" )
				return
			
			for client in globals.ottd_clients:
				if globals.ottd_clients[client]['company'] == (id - 1):
					globals.openttd.rcon_cmd(f'move {client} 255')

			globals.openttd.rcon_cmd(f'reset_company {id}')
		except:
			await ctx.channel.send( "An error occured" )
			


	@bot.command()
	async def rcon(ctx, *, command):
		if command.startswith("reset_company"):
			await ctx.channel.send( "Err: please use !reset <company_id>" )
			return
		
		globals.openttd.rcon_cmd(command)

	
	@bot.command()
	async def clean(ctx, channel_name, count):
		try:
			count = int(count)

			for channel in ctx.channel.guild.channels:
				if channel.name == channel_name:
					messages = [message async for message in channel.history(limit=count)]

					for message in messages:
						await message.delete()
					# begin = 0
					# end = count
					# if count > 100: end = 100

					# while end < count:
					# 	await channel.delete_messages(messages[begin:end] )
					# 	begin = end
					# 	remaining = count - end
						
					# 	if remaining < 0: break

					# 	if remaining > 100: end += 100
					# 	else: end += remaining
						

					await ctx.channel.send( f"Deleted {count} messages from {channel_name}" )
					return
			
			await ctx.channel.send( "Channel not managed by bot" )
			
		except Exception as e:
			print(e)
			await ctx.channel.send( "somethings not right" )
	



		# header = [x[0] for x in res[0]._fields_]
		# rows =  [ ctypes_values_list(x) for x in res]

		# await ctx.channel.send( tabulate(rows, header) )






		# header = [x[0] for x in res[0]._fields_]
		# rows =  [ ctypes_values_list(x) for x in res]

		# await ctx.channel.send( tabulate(rows, header) )
	
	
		




'''
=================================================
'''
def on_discord_admin_message(message ):
	globals.openttd.chat_external('discord','admin', str(message.content), ottdenum.TextColor.TC_RED )
	


def on_discord_message(message):
	globals.openttd.chat_external('discord', str(message.author), str(message.content))


