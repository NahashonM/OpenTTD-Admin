
import threading
import asyncio
import discord

from discord.ext import commands
from discord.message import Message

import globals



#
#
class DiscordBot(commands.Bot):
	def __init__(self, server_name, admin_channel, ingame_channel, intents: discord.Intents, **options: any ) -> None:
		super().__init__(intents=intents, **options)

		self.server_name = server_name
		self.admin_channel_name = admin_channel
		self.ingame_channel_name = ingame_channel	

		self.guild_id = None
		self.admin_channel_id = None
		self.ingame_channel_id = None

		self.on_ingame_channel_message = []
		self.on_admin_channel_message = []



    # init guilds and channels
	async def on_ready(self):
		for guild in self.guilds:
			if guild.name != self.server_name:
				continue

			for channel in guild.channels:
				
				if channel.name == self.admin_channel_name:
					self.admin_channel_id = channel.id

				elif channel.name == self.ingame_channel_name:
					self.ingame_channel_id = channel.id

			print(f"connected to {guild.name}:[{guild.id}] as user {self.user}")
			print(f"\t admin channel: {self.admin_channel_name}:[{self.admin_channel_id}]")
			print(f"\t ingame channel: {channel.name }:[{self.ingame_channel_id}]")

			break

	async def on_message(self, message):

		if message.author == self.user:	return

		ctx = await self.get_context(message)
		if message.channel.id == self.admin_channel_id:
			
			# process commands
			if ctx.valid and ctx.command:
				await self.process_commands(message)
				return
			
			# process admin messages
			for callback in self.on_admin_channel_message: 
				callback(message)

			return
		
		if message.channel.id != self.ingame_channel_id: return
		
		# process ingame messages
		for callback in self.on_ingame_channel_message:
			callback(message)

	
	def register_on_admin_message_callback(self, callback):
		self.on_admin_channel_message.append( callback )

	def register_on_ingame_message_callback(self, callback):
		self.on_ingame_channel_message.append( callback )



	async def send_message_to_admin_channel(self, message):
		admin_channel = self.get_channel(self.admin_channel_id)
		await admin_channel.send(message)

	async def send_message_to_ingame_channel(self, message):
		ingame_channel = self.get_channel(self.ingame_channel_id)
		await ingame_channel.send(message)
	



def run_discord_async_function( function ):
	return asyncio.run_coroutine_threadsafe(  function , globals.discord_bot.loop)




# intents = discord.Intents.default()
# intents.message_content = True

# bot = DiscordBot(discord_guild, admin_channel_name, ingame_channel_name, intents=intents)
# bot.run(discord_token)


# bot.send_message_to_admin_channel("Hello ")


# #----------- guild events --------------------------
# async def on_guild_join( guild ):
# 	pass

# async def on_guild_remove( guild ):
# 	pass

# async def on_guild_available( guild ):				# --
# 	pass

# async def on_guild_unavailable( guild ):			# --
# 	pass

# async def on_guild_update( before, after ):			# --
# 	pass

# #----------- thread events --------------------------
# async def on_thread_create( guild ):
# 	pass

# async def on_thread_join( guild ):
# 	pass

# async def on_thread_update( guild ):
# 	pass

# async def on_thread_remove( guild ):
# 	pass
