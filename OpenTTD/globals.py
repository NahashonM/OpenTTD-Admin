
# global bot for discord communication and control
#-------------------------------------------------
discord_bot = None


# Global OpenTTD admin clients 
#     poll admin : updates on query
#  update admin  : automatic updates
#-------------------------------------------------
ottdPollAdmin = None
ottdUpdateAdmin = None


# Global OpenTTD structures 
#      ottd_clients : players currently in the game
#    ottd_companies : companies currently in the game
#------------------------------------------------- 
ottd_clients = {}
ottd_companies = {}


#
#-------------------------------------------------
serverWelcome = None