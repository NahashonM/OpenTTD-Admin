


from OpenTTD.network.packet_types import PacketAdminJoin
from OpenTTD.network.packet import Packet
from OpenTTD.enums import *
from OpenTTD.date import Date

from OpenTTD.openttd import OpenTTD

from threading import Thread
import time


def OpenTTD_Main():

	print(" get data")
	data = game.poll_client_infor()
	print(data)
	print("done")

	i = 0
	# while True:
	# 	game.chat_all("Test")
	# 	data = game.server_listen()
	# 	print(data)
	# 	i += 1

	# 	if( i >= 2):
	# 		break
	# 	time.sleep(1)

	print("Thread exit")



game = OpenTTD('127.0.0.1', 3977, "Admin", '!@Admin123')
game.connect()



thread = Thread(target = OpenTTD_Main, args = ())
thread.start()
thread.join()

print("Other exit")



