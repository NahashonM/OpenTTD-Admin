import discord


DISCORD_TOKEN = 'OTg3MzU3NDMzODU5MDIyOTI5.G9iwou.sUo5NBYiBY3OLbiJu2vDDh5Okghd3YzanFkueE'
DISCORD_GUILD = 'OpenTTD_HappyDays'

DISCORD_ADMIN_CHANNEL_ID = '1026123801794187304'
DISCORD_GAME_CHANNEL = ''

class DiscordChannel:
	def __init__(self, AuthToken) -> None:
		pass

# token
# admin_channel
# chat_channel



class OpenTTDGame:
	def __init__(self, srvr_name: str, srvr_ip_admin_port: tuple, srvr_admin_name: str, srvr_admin_password: str):
		self.server_name = srvr_name
		self.server_ip = srvr_ip_admin_port[0]

		self.server_admin_port = srvr_ip_admin_port[1]

		self.server_admin_name = srvr_admin_name
		self.server_admin_password = srvr_admin_password


class DiscordBot(discord.Client):
	def __init__(self, admin_channel_id, intents: discord.Intents, **options: any) -> None:
		super().__init__(intents=intents, **options)

	async def on_ready(self):
		print(f'Logged in as {self.user}!')

	async def on_message(self, message):
		if message.author == self.user or message.channel.id != DISCORD_ADMIN_CHANNEL_ID:
			return
		
		print(f'Message from {message.author}: {message.content}')
		await message.channel.send('Hello!')



intents = discord.Intents.default()
intents.message_content = True

bot = Bot(intents=intents)


bot.run(DISCORD_TOKEN)
