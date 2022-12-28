Class TCPSocket:

	---Properties---
	ip_addr
	port
	
	---Methods---
	connect()
	reconnect()
	disconnect()
	
	send_data()
	receive_data()


class DataPacket:
	---Static Methods---
	bytes_to_bool()
	bytes_to_int()
	bytes_to_str()
	
	bool_to_bytes()
	int_to_bytes()
	str_to_bytes()
	
	bool_from_bytes()
	int_from_bytes()
	str_from_bytes()


class EntityPackets: -> Client, Company, Stats
	---Properties---
	...
	
	---Methods---
	parse_from_bytes()		-> data receivers
	to_bytes()				-> data senders

class OpenTTD: