'''

'''
import os
import time
import pika
import logging
import threading
import argparse

import rabbitmq as rmq

import openttd.openttd as ottd
import openttd.ottd_enum as ottdtypes


logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("main")

def parse_cmd_arguments():
    parser = argparse.ArgumentParser(
                    prog = os.path.basename(__file__),
                    description = 'OpenTTD Admin client',
                    epilog = 'To report any bugs reach out to the dev via email: nahashonm386@gmail.com.')
    
    parser.add_argument('-s', '--server', type=str,
                        metavar='ip:admin-port',
                        default="127.0.0.1:3977", 
                        help="Game server ip and port. Default=127.0.0.1:3977")
    
    parser.add_argument('-r', '--rabbitmq', type=str,
                        metavar='ip:port',
                        default="127.0.0.1:5672", 
                        help="RabbitMQ server ip and port. Default=127.0.0.1:5672")
    
    parser.add_argument('-u', '--user', type=str,
                        metavar='name',
                        default="admin", 
                        help="text to use as username when connecting to OpenTTD admin port. Default=admin")
    
    parser.add_argument('-p', '--pswd', type=str,
                        metavar='pswd', 
                        default="!@Admin123", 
                        help="Password configured for the admin port in OpenTTD. Default is empty password")

    return parser.parse_args()



def control_queue_callback(ch, method, properties, body):
	response = body.decode()

	print("\nresponse = " + response)



if __name__ == "__main__":
	args = parse_cmd_arguments()

	# rabbit_host, rabbit_port = args.rabbitmq.split(':')

	# mq = rmq.RabbitMQ(rabbit_host, rabbit_port)
	# mq.clean_up()
	# mq.create_queue_exchange()
	# mq.register_msg_callback(control_queue_callback)
	# mq.start_consuming()

	ottd_host, ottd_admin_port = args.server.split(':')
	ottd_admin = ottd.OpenTTDAdmin(ottd_host, ottd_admin_port, args.user, args.pswd)

	ottd_admin.join_server()

	#print(ottd_admin.ping_server())
	#print(ottd_admin.poll_current_date())
	#print(ottd_admin.poll_client_info()[1].name)
	#print(ottd_admin.poll_company_info()[0].name)
	#print(ottd_admin.poll_company_economy()[0].loan)
	#print(ottd_admin.poll_company_stats()[0].vehicles)
	ottd_admin.chat_all("Hello World")
	#ottd_admin.chat_client(32,"Hello World")
	#ottd_admin.chat_team(0,"Hello World")
	#ottd_admin.chat_external("discord","Nahashon","Hello World")

	#ottd_admin.rcon_cmd("set yapf.rail_firstred_twoway_eol true")

	ottd_admin.request_date_updates(ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY)
	#ottd_admin.request_client_info_updates(ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC)
	#ottd_admin.request_company_economy_updates(ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC)
	ottd_admin.request_company_info_updates()
	#ottd_admin.request_company_stats_updates(ottdtypes.AdminUpdateFrequency.ADMIN_FREQUENCY_ANUALLY)


	while True:
		updates = ottd_admin.get_registered_updates()
		for update in updates:
			if type(update) == list:
				for entry in update:
					print("\t ", entry.__dict__)
			else:
				print( update.__dict__)
		
		print("--------------")

		time.sleep(0.1)

	

	# Updates continuing on main thread

	exit(0)


logger.warning("This file is not intended to be a module but a main application")