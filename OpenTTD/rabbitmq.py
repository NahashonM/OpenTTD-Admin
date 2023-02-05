'''

'''

import pika
import logging
from pika.exceptions import *

mglog = logging.getLogger("RabbitMQ")

class RabbitMQ:
	def __init__(self, server_ip, server_port) -> None:
		self.server_ip = server_ip
		self.server_port = server_port

		self.ctrl_queue_name = f"QCTRL-{server_ip}:{server_port}"
		self.update_queue_name = f"QUPDT-{server_ip}:{server_port}"

		self.exchange_name = f"EX-{server_ip}:{server_port}"

		mglog.info(f"Connecting to {server_ip}:{server_port}")

		try:
			connection_params = pika.ConnectionParameters(host=self.server_ip, port=self.server_port)
			self.connection = pika.BlockingConnection(connection_params)
			self.channel = self.connection.channel()
		except:
			mglog.critical(f"Failed to connect to {server_ip}:{server_port}\n---------EXITING---------")
			exit(0)
	

	def __create_queue__(channel, queue_name:str):
		mglog.info(f"Creating queue {queue_name}")
		return channel.queue_declare( queue=queue_name, 
									  auto_delete=True, arguments={"x-expires": 600000, "x-message-ttl": 4000})


	def __create_exchange__(channel, exchange_name:str):
		mglog.info(f"Creating exchange {exchange_name}")
		return channel.exchange_declare( exchange=exchange_name, exchange_type='topic', 
										 auto_delete=True, arguments={"x-expires": 600000, "x-message-ttl": 4000})


	def __bind_queue_exchange__(channel, queue_name:str, exchange_name:str, key:str):
		mglog.info(f"Topic Binding for Exchange {exchange_name} and Queue {queue_name}")
		channel.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=key)


	def __delete_queue_if_exists__(channel, queue_name:str):
		mglog.warning(f"Cleaning queue {queue_name}")
		try:
			channel.queue_delete(queue_name)
		except (pika.exceptions.ChannelClosedByBroker) as e:
			pass
	

	def __delete_exchange_if_exists__(channel, exchange_name:str):
		mglog.warning(f"Cleaning exchange {exchange_name}")
		try:
			channel.exchange_delete(exchange_name)
		except (pika.exceptions.ChannelWrongStateError) as e:
			pass
	
	
	def create_queue_exchange(self):
		try:
			RabbitMQ.__create_queue__(self.channel, self.ctrl_queue_name)
			RabbitMQ.__create_queue__(self.channel, self.update_queue_name)
			RabbitMQ.__create_exchange__(self.channel, self.exchange_name)

			RabbitMQ.__bind_queue_exchange__(self.channel, self.ctrl_queue_name, self.exchange_name, "control.#")
			RabbitMQ.__bind_queue_exchange__(self.channel, self.update_queue_name, self.exchange_name, "update.#")

		except Exception as e:
			mglog.critical(f"Queue Exchange Binding Failed:\n\t[Exception] {e}\n---------EXITING---------")
			exit(0)
	

	def clean_up(self):
		try:
			RabbitMQ.__delete_queue_if_exists__(self.channel, self.ctrl_queue_name)
			RabbitMQ.__delete_queue_if_exists__(self.channel, self.update_queue_name)
			RabbitMQ.__delete_exchange_if_exists__(self.channel, self.exchange_name)
			
			mglog.info("Cleaning complete or nothing to be done")
		except Exception as e:
			mglog.critical(f"Failed to Clean up old queue and exchange:\n\t[Exception]{type(e)} {e}\n---------EXITING---------")
			exit(0)
	
	
	def control_queue_callback(self, ch, method, properties, body):
		response = body.decode()

		self.publish_message("update", f"response to {response}")

		print("\nresponse = " + response)

	

	def publish_message(self, key, message):
		self.channel.basic_publish( exchange=self.exchange_name, routing_key=key, body=message)
		
	
	def start_consuming(self):
		self.channel.start_consuming()


	def register_msg_callback(self, callback, tag = "admin"):
		self.channel.basic_consume( queue=self.ctrl_queue_name, 
									on_message_callback=callback, auto_ack=True, consumer_tag="admin")
