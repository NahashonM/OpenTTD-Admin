"""
	Dependencies
		python-dotenv
"""
import os
import discord

from dotenv import load_dotenv

load_dotenv()


discord_token = os.getenv("DISCORD_TOKEN")
discord_guild = os.getenv("DISCORD_GUILD")  # servers

admin_channel_name = os.getenv("DISCORD_ADMIN_CHANNEL")
ingame_channel_name = os.getenv("DISCORD_INGAME_CHANNEL")


# token
# admin_channel
# chat_channel


#
#
class DiscordBot(discord.Client):
	def __init__(self, server_name, admin_channel, ingame_channel, intents: discord.Intents, **options: any ) -> None:
		super().__init__(intents=intents, **options)

		self.server_name = server_name
		self.admin_channel_name = admin_channel
		self.ingame_channel_name = ingame_channel	

		self.guild_id = None
		self.admin_channel_id = None
		self.ingame_channel_id = None

		self.on_message_callbacks = []

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
		if message.author == self.user or not (message.channel.id == self.ingame_channel_id or message.channel.id == self.admin_channel_id):
			return
		
		for callback in self.on_message_callbacks:
			callback(message)

		print(f"Message from {message.author}: {message.content} channel: {message.channel}")
        # await message.channel.send('Hello!')

		await self.send_message_to_admin_channel("hello world")
	
	def register_on_message_callback(self, callback):
		pass

	async def send_message_to_admin_channel(self, message):
		admin_channel = self.get_channel(self.admin_channel_id)
		await admin_channel.send(message)


	async def send_message_to_ingame_channel(self, message):
		ingame_channel = self.get_channel(self.ingame_channel_id)
		await ingame_channel.send(message)
	



intents = discord.Intents.default()
intents.message_content = True

bot = DiscordBot(discord_guild, admin_channel_name, ingame_channel_name, intents=intents)
bot.run(discord_token)


bot.send_message_to_admin_channel("Hello ")


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
