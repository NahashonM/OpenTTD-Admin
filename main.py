


from OpenTTD.network.packet_types import PacketAdminJoin
from OpenTTD.network.packet import Packet
from OpenTTD.enums import *
from OpenTTD.date import Date

from OpenTTD.openttd import OpenTTD



game = OpenTTD('127.0.0.1', 3977, "Admin", '!@Admin123')
game.connect()

