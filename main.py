

from threading import Thread

from openttd.openttd import OpenTTD

game = OpenTTD('127.0.0.1', 3977, "Admin", '!@Admin123')
game.join()
game.chat_all("All_chat")
game.chat_team(255, "Team_chat")
game.chat_client(3, "Client_chat")
game.chat_external("Discord", "admin", "external", 0)


print( game.poll_current_date() )
print("--------------------")

data = game.poll_client_info()
for d in data:
	print( d.id, d.address ,d.name, d.lang,d.join_date,d.company)
print("--------------------")

data = game.poll_company_info()
for d in data:
	print( d.id, d.name, d.president, d.color,
			d.has_password, d.start_date, d.is_ai, d.quaters_bankrupt, d.share_owners)
print("--------------------")

data = game.poll_company_economy()
for d in data:
	print(d.id, d.money, d.loan, d.income, d.delivered_cargo, d.quarters)
print("--------------------")

data = game.poll_company_stats()
for d in data:
	print(d.id, d.vehicles, d.stations)
print("--------------------")


# 	print("Thread exit")



# game = OpenTTD('127.0.0.1', 3977, "Admin", '!@Admin123')
# game.connect()



# thread = Thread(target = OpenTTD_Main, args = ())
# thread.start()
# thread.join()

# print("Other exit")



