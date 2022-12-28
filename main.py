

from threading import Thread

from openttd.tcpsocket import TCPSocket

sok = TCPSocket('127.0.0.1', 3977)
#sok = TCPSocket('google.com', 80)
sok.connect()
sok.reconnect()


sok.receive_data()

# def OpenTTD_Main():

# 	data = game.poll_client_info()

# 	for d in data:
# 		print( d.id, d.address ,d.name, d.lang,d.join_date,d.company)

# 	# print("--------------------")

# 	# data = game.poll_company_info()
# 	# for d in data:
# 	# 	print( d.id, d.name, d.president, d.color,
# 	# 		d.has_password, d.start_date, d.is_ai, d.quaters_bankrupt,
# 	# 		d.share_owners)

# 	# # print("--------------------")

# 	# # data = game.poll_current_date()
# 	# # print(data)

# 	# # print("--------------------")

# 	# # data = game.poll_company_economy()
# 	# # for d in data:
# 	# # 	print(d.id, d.money, d.loan, d.income, d.delivered_cargo, d.quarters)

# 	# # print("--------------------")

# 	# data = game.poll_company_stats()
# 	# for d in data:
# 	# 	print(d.id, d.vehicles, d.stations)

# 	# print("--------------------")


# 	print("Thread exit")



# game = OpenTTD('127.0.0.1', 3977, "Admin", '!@Admin123')
# game.connect()



# thread = Thread(target = OpenTTD_Main, args = ())
# thread.start()
# thread.join()

# print("Other exit")



