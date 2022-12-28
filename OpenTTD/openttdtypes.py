from enum import IntEnum

ADMIN_CLIENT_VERSION = 'v0.0.1'

MAX_UINT = 0xFFFFFFFF

MAX_COMPANY_SHARE_OWNERS	= 4
ECONOMY_INFO_QUARTERS		= 2
INVALID_PACKET 				= 255

MONTH_DAYS = {
	"JAN": 31, "FEB": 28, "MAR": 31, "APR": 30, 
	"MAY": 31, "JUN": 30, "JUL": 31, "AUG": 31,
	"SEP": 30, "OCT": 31, "NOV": 30, "DEC": 31
	}



class PacketAdminType(IntEnum):
	ADMIN_PACKET_ADMIN_JOIN				=0 	# The admin announces and authenticates itself to the server.
	ADMIN_PACKET_ADMIN_QUIT				=1	# The admin tells the server that it is quitting.
	ADMIN_PACKET_ADMIN_UPDATE_FREQUENCY	=2	# The admin tells the server the update frequency of a particular piece of information.
	ADMIN_PACKET_ADMIN_POLL				=3	# The admin explicitly polls for a piece of information.
	ADMIN_PACKET_ADMIN_CHAT				=4	# The admin sends a chat message to be distributed.
	ADMIN_PACKET_ADMIN_RCON				=5	# The admin sends a remote console command.
	ADMIN_PACKET_ADMIN_GAMESCRIPT		=6	# The admin sends a JSON string for the GameScript.
	ADMIN_PACKET_ADMIN_PING				=7	# The admin sends a ping to the server, expecting a ping-reply (PONG) packet.
	ADMIN_PACKET_ADMIN_EXTERNAL_CHAT	=8	# The admin sends a chat message from external source.

	ADMIN_PACKET_SERVER_FULL 			=100	# The server tells the admin it cannot accept the admin.
	ADMIN_PACKET_SERVER_BANNED			=101	# The server tells the admin it is banned.
	ADMIN_PACKET_SERVER_ERROR			=102	# The server tells the admin an error has occurred.
	ADMIN_PACKET_SERVER_PROTOCOL		=103	# The server tells the admin its protocol version.
	ADMIN_PACKET_SERVER_WELCOME			=104	# The server welcomes the admin to a game.
	ADMIN_PACKET_SERVER_NEWGAME			=105	# The server tells the admin its going to start a new game.
	ADMIN_PACKET_SERVER_SHUTDOWN		=106	# The server tells the admin its shutting down.

	ADMIN_PACKET_SERVER_DATE			=107		# The server tells the admin what the current game date is.
	ADMIN_PACKET_SERVER_CLIENT_JOIN		=108		# The server tells the admin that a client has joined.
	ADMIN_PACKET_SERVER_CLIENT_INFO		=109		# The server gives the admin information about a client.
	ADMIN_PACKET_SERVER_CLIENT_UPDATE	=110		# The server gives the admin an information update on a client.
	ADMIN_PACKET_SERVER_CLIENT_QUIT		=111		# The server tells the admin that a client quit.
	ADMIN_PACKET_SERVER_CLIENT_ERROR	=112		# The server tells the admin that a client caused an error.
	ADMIN_PACKET_SERVER_COMPANY_NEW		=113		# The server tells the admin that a new company has started.
	ADMIN_PACKET_SERVER_COMPANY_INFO	=114		# The server gives the admin information about a company.
	ADMIN_PACKET_SERVER_COMPANY_UPDATE	=115		# The server gives the admin an information update on a company.
	ADMIN_PACKET_SERVER_COMPANY_REMOVE	=116		# The server tells the admin that a company was removed.
	ADMIN_PACKET_SERVER_COMPANY_ECONOMY	=117		# The server gives the admin some economy related company information.
	ADMIN_PACKET_SERVER_COMPANY_STATS	=118		# The server gives the admin some statistics about a company.
	ADMIN_PACKET_SERVER_CHAT			=119		# The server received a chat message and relays it.
	ADMIN_PACKET_SERVER_RCON			=120		# The server's reply to a remove console command.
	ADMIN_PACKET_SERVER_CONSOLE			=121		# The server gives the admin the data that got printed to its console.
	ADMIN_PACKET_SERVER_CMD_NAMES		=122		# The server sends out the names of the DoCommands to the admins.
	ADMIN_PACKET_SERVER_CMD_LOGGING_OLD	=123		# Used to be the type ID of \c ADMIN_PACKET_SERVER_CMD_LOGGING in \c NETWORK_GAME_ADMIN_VERSION 1.
	ADMIN_PACKET_SERVER_GAMESCRIPT		=124		# The server gives the admin information from the GameScript in JSON.
	ADMIN_PACKET_SERVER_RCON_END		=125		# The server indicates that the remote console command has completed.
	ADMIN_PACKET_SERVER_PONG			=126		# The server replies to a ping request from the admin.
	ADMIN_PACKET_SERVER_CMD_LOGGING		=127		# The server gives the admin copies of incoming command packets.
	INVALID_ADMIN_PACKET 				=255		# An invalid marker for admin packets.



# Status of an admin. */
class AdminStatus(IntEnum):
	ADMIN_STATUS_INACTIVE	= 0					# The admin is not connected nor active.
	ADMIN_STATUS_ACTIVE	 	= 1					# The admin is active.
	ADMIN_STATUS_END	 	= 2					# Must ALWAYS be on the end of this list!! (period)



# Update types an admin can register a frequency for */
class AdminUpdateType(IntEnum):
	ADMIN_UPDATE_DATE				=0		# Updates about the date of the game.
	ADMIN_UPDATE_CLIENT_INFO		=1		# Updates about the information of clients.
	ADMIN_UPDATE_COMPANY_INFO		=2		# Updates about the generic information of companies.
	ADMIN_UPDATE_COMPANY_ECONOMY	=3		# Updates about the economy of companies.
	ADMIN_UPDATE_COMPANY_STATS		=4		# Updates about the statistics of companies.
	ADMIN_UPDATE_CHAT				=5		# The admin would like to have chat messages.
	ADMIN_UPDATE_CONSOLE			=6		# The admin would like to have console messages.
	ADMIN_UPDATE_CMD_NAMES			=7		# The admin would like a list of all DoCommand names.
	ADMIN_UPDATE_CMD_LOGGING		=8		# The admin would like to have DoCommand information.
	ADMIN_UPDATE_GAMESCRIPT			=9		# The admin would like to have gamescript messages.
	ADMIN_UPDATE_END				=10		# Must ALWAYS be on the end of this list!! (period)



# Update frequencies an admin can register. */
class AdminUpdateFrequency(IntEnum):
	ADMIN_FREQUENCY_POLL      = 0x01					# The admin can poll this.
	ADMIN_FREQUENCY_DAILY     = 0x02					# The admin gets information about this on a daily basis.
	ADMIN_FREQUENCY_WEEKLY    = 0x04					# The admin gets information about this on a weekly basis.
	ADMIN_FREQUENCY_MONTHLY   = 0x08					# The admin gets information about this on a monthly basis.
	ADMIN_FREQUENCY_QUARTERLY = 0x10					# The admin gets information about this on a quarterly basis.
	ADMIN_FREQUENCY_ANUALLY   = 0x20					# The admin gets information about this on a yearly basis.
	ADMIN_FREQUENCY_AUTOMATIC = 0x40					# The admin gets information about this when it changes.



# Reasons for removing a company - communicated to admins. */
class AdminCompanyRemoveReason(IntEnum):
	ADMIN_CRR_MANUAL	=0		# The company is manually removed.
	ADMIN_CRR_AUTOCLEAN	=1		# The company is removed due to autoclean.
	ADMIN_CRR_BANKRUPT	=2		# The company went belly-up.
	ADMIN_CRR_END		=3		# Sentinel for end.


class NetworkVehicleType(IntEnum):
	NETWORK_VEH_TRAIN	= 0
	NETWORK_VEH_LORRY	= 1
	NETWORK_VEH_BUS		= 2
	NETWORK_VEH_PLANE	= 3
	NETWORK_VEH_SHIP	= 4
	NETWORK_VEH_END		= 5


class ServerGameType(IntEnum):
	SERVER_GAME_TYPE_LOCAL = 0
	SERVER_GAME_TYPE_PUBLIC = 1
	SERVER_GAME_TYPE_INVITE_ONLY = 2


class ClientID(IntEnum):
	INVALID_CLIENT_ID = 0	#< Client is not part of anything
	CLIENT_ID_SERVER  = 1	#< Servers always have this ID
	CLIENT_ID_FIRST   = 2	#< The first client ID



class NetworkAction(IntEnum):
	NETWORK_ACTION_JOIN				=0
	NETWORK_ACTION_LEAVE			=1
	NETWORK_ACTION_SERVER_MESSAGE	=2
	NETWORK_ACTION_CHAT				=3
	NETWORK_ACTION_CHAT_COMPANY		=4
	NETWORK_ACTION_CHAT_CLIENT		=5
	NETWORK_ACTION_GIVE_MONEY		=6
	NETWORK_ACTION_NAME_CHANGE		=7
	NETWORK_ACTION_COMPANY_SPECTATOR=8
	NETWORK_ACTION_COMPANY_JOIN		=9
	NETWORK_ACTION_COMPANY_NEW		=10
	NETWORK_ACTION_KICKED			=11
	NETWORK_ACTION_EXTERNAL_CHAT	=12


class DestType(IntEnum):
	DESTTYPE_BROADCAST	=0			# < Send message/notice to all clients (All)
	DESTTYPE_TEAM		=1			# < Send message/notice to everyone playing the same company (Team)
	DESTTYPE_CLIENT		=2			# < Send message/notice to only a certain client (Private)


CHAT_MAP = [
	(NetworkAction.NETWORK_ACTION_CHAT,  DestType.DESTTYPE_BROADCAST),
	(NetworkAction.NETWORK_ACTION_CHAT_CLIENT, DestType.DESTTYPE_CLIENT),
	(NetworkAction.NETWORK_ACTION_CHAT_COMPANY, DestType.DESTTYPE_TEAM)
]

class CHAT_TYPE(IntEnum):
	ALL = 0
	CLIENT = 1
	COMPANY = 2
	EXTERNAL = 3

class TextColor(IntEnum):
	TC_BEGIN       = 0x00
	TC_FROMSTRING  = 0x00
	TC_BLUE        = 0x00
	TC_SILVER      = 0x01
	TC_GOLD        = 0x02
	TC_RED         = 0x03
	TC_PURPLE      = 0x04
	TC_LIGHT_BROWN = 0x05
	TC_ORANGE      = 0x06
	TC_GREEN       = 0x07
	TC_YELLOW      = 0x08
	TC_DARK_GREEN  = 0x09
	TC_CREAM       = 0x0A
	TC_BROWN       = 0x0B
	TC_WHITE       = 0x0C
	TC_LIGHT_BLUE  = 0x0D
	TC_GREY        = 0x0E
	TC_DARK_BLUE   = 0x0F
	TC_BLACK       = 0x10
	TC_END		   = 0x11
	TC_INVALID     = 0xFF,
	TC_IS_PALETTE_COLOUR = 0x100	# Colour value is already a real palette colour index, not an index of a StringColour.
	TC_NO_SHADE          = 0x200	# Do not add shading to this text colour.
	TC_FORCED            = 0x400	# Ignore colour changes from strings.


class Color(IntEnum):
	COLOUR_BEGIN		=0
	COLOUR_DARK_BLUE 	=0
	COLOUR_PALE_GREEN	=1
	COLOUR_PINK			=2
	COLOUR_YELLOW		=3
	COLOUR_RED			=4
	COLOUR_LIGHT_BLUE	=5
	COLOUR_GREEN		=6
	COLOUR_DARK_GREEN	=7
	COLOUR_BLUE			=8
	COLOUR_CREAM		=9
	COLOUR_MAUVE		=10
	COLOUR_PURPLE		=11
	COLOUR_ORANGE		=12
	COLOUR_BROWN		=13
	COLOUR_GREY			=14
	COLOUR_WHITE		=15
	COLOUR_END			=16
	INVALID_COLOUR		= 0xFF
