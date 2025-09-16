
from dotenv import load_dotenv
import os, logging
import time

from ottd import OTTDEnums
from ottd.OTTDBot import OTTDBot

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

srvr_ip = os.getenv("SERVER_IP")
srvr_port = os.getenv("SERVER_PORT")
admin_name = os.getenv("ADMIN_CLIENT_NAME")
admin_password = os.getenv("ADMIN_CLIENT_PASSWORD")

try:
    srvr_port=int(srvr_port)
except:
    logger.error("Invalid server port")
    exit(0)

bot = OTTDBot(srvr_ip, srvr_port)
bot.join_game(admin_name, admin_password)

players = {}
companies = {}

@bot.packet_handler(packet_type='ClientInfo')
def client_info_handler(packet):
    players[packet.id] = {
            "name": packet.name.decode('utf-8'), 
            "company": packet.company
        }

@bot.packet_handler(packet_type='ClientUpdate')
def client_update_handler(packet):
    players[packet.id] = {
            "name": packet.name.decode('utf-8'), 
            "company": packet.company
        }

@bot.packet_handler(packet_type='ClientQuit')
def client_quit_handler(packet):
    if packet.id in players:
        del players[packet.id]

# ------------------------------------------------- #

@bot.packet_handler(packet_type='CompanyNew')
def company_new_handler(packet):
    companies[packet.id] = {
            "name": "Unnamed", 
            "is_protected": False
        }
    
@bot.packet_handler(packet_type='CompanyInfo')
def company_info_handler(packet):
    companies[packet.id] = {
            "name": packet.name.decode('utf-8'), 
            "is_protected": packet.is_protected
        }

@bot.packet_handler(packet_type='CompanyUpdate')
def company_update_handler(packet):
    companies[packet.id] = {
            "name": packet.name.decode('utf-8'), 
            "is_protected": packet.is_protected
        }

@bot.packet_handler(packet_type='CompanyRemove')
def company_remove_handler(packet):
    if packet.id in companies:
        del companies[packet.id]

# ------------------------------------------------- #

@bot.packet_handler(packet_type='ServerNewGame')
def server_new_game_handler(packet):
    global players
    global companies

    players = {}
    companies = {}

    bot.poll(OTTDEnums.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO)
    bot.poll(OTTDEnums.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO)



# ------------------------------------------------- #

@bot.chat_command(command="reset", help="Reset/Wipe/Delete your company.")
def reset(command, args, src):
    player = players[src]
    
    player_id = src
    
    player = players.get(src)
    player_name = player.get("name")
    player_company = player.get("company")
    if player is None or player_company is None:
        bot.chat_client(src, "!..Please try again in a few seconds..!")
        return
    
    if player_company == 255:
        bot.chat_client(player_id, "You cannot do that as a spectator..!")
        return
    
    teammate_count = 0
    for plyr_id in players:
        plyr = players.get(plyr_id)
        if plyr is None: continue

        plyr_company = plyr.get("company")
        if plyr_company is None: continue

        if plyr_company == player_company: teammate_count += 1
        if teammate_count > 1: break

    if teammate_count > 1:
        bot.chat_client(src, "You cannot do that while other teammates are joined..!")
        return
    
    print(f"reset_company {player_company+1}")
    pkt_move = bot.send_factory.rcon_packet(f"move {src} 255")
    pkt_del = bot.send_factory.rcon_packet(f"reset_company {player_company+1}")

    bot.send( pkt_move.to_bytes() )
    bot.send( pkt_del.to_bytes() )



@bot.chat_command(command="rules", help="View house rules.")
def rules(command, args, src):
    bot.chat_client(src, '************ Rules ************')
    bot.chat_client(src, " Respect other players.")
    bot.chat_client(src, " Don't intentionally block other players.")
    bot.chat_client(src, '  ')


@bot.chat_command(command="help", help="Scream at the admin..!")
def help(command, args, src):
    bot.chat_client(src, '************ Help ************')
    for help_msg in bot.get_help_messages():
        bot.chat_client(src, help_msg)
    
    bot.chat_client(src, '  ')
    bot.chat_client(src, '  -- Reset date: 2052 --')
    bot.chat_client(src, '  ')


# ------------------------------------------------- #

last_tick = None
poll_interval_s = 120

@bot.bot_tick()
def handle_bot_tick():
    global last_tick
    global poll_interval_s

    current_tick = time.time()
    if last_tick is None or (current_tick - last_tick) >= poll_interval_s:
        bot.poll(OTTDEnums.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO)
        bot.poll(OTTDEnums.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO)

    last_tick = time.time()

# ------------------------------------------------- #

# bot.subscribe(OTTDEnums.AdminUpdateType.ADMIN_UPDATE_DATE, OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY)
bot.subscribe(OTTDEnums.AdminUpdateType.ADMIN_UPDATE_CHAT, OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC)
bot.subscribe(OTTDEnums.AdminUpdateType.ADMIN_UPDATE_CLIENT_INFO, OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC)
bot.subscribe(OTTDEnums.AdminUpdateType.ADMIN_UPDATE_COMPANY_INFO, OTTDEnums.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC)

bot.run()


