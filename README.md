
# OpenTTD Admin Client
A tool to make it easier for OpenTTD Administrators to easily manage one or multiple servers.


# Usage

# Components
1. openttd admin client:
	middle man for all communication between the client tools and the OpenTTD server
	publishes all messages from the server to RabbitMQ queue
	consumes control messages in RabbitMQ queue from client tools

1. RabbitMQ
	broke messages between client tools and the openttd admin client
	CONTROL_<server_ip>:<admin_port>
		queue for client tools to publish control messages consumed by the admin client

	UPDATE_<server_ip>:<admin_port>
		queue for the admin client to publish messages for consumption by the client tools

# Requirements
1. Python3
1. Pika
1. RabbitMQ