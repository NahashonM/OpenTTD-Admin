# Classes and Class Methods and Functions
## class OTTDSocket:
	def __init__(self, server_ip, admin_port, timeout = 0.3) -> None:
	def connect(self):
	def disconnect(self):
	def send_data(self, data: bytearray) -> bool:
	def peek(self,*, num_bytes: int = 3, retries: int= 1):
	def receive_data(self, buffer_size):

## util
	int_to_bytes(int_value: int, byte_count:int, separator: bytes = b'\x00') -> bytearray:
	str_to_bytes(str_value:str, separator: bytes = b'\x00') -> bytearray:
	bytes_to_int(byte_value: bytearray, signed=False) -> int:
	bytes_to_str(byte_value: bytearray) -> str:
	bytes_to_bool(byte_value: bytearray) -> bool:
	get_int_from_bytes(byte_value: bytearray, int_size: int, *, signed=False):
	get_bool_from_bytes(byte_value: bytearray, bool_size: int = 1):
	get_str_from_bytes(byte_value: bytearray) -> bool:
	get_type_from_packet(raw_bytes):
	get_length_from_packet(raw_bytes):
	ConvertYMDToDate(year, month, day):
	ConvertDateToYMD(date):


## class OpenTTDAdmin:
	__init__(self, server_ip, admin_port, admin_name, admin_pswd) -> None:
	join_server(self):
	leave_server(self):
	ping_server(self) -> bool:
	poll_current_date(self) -> tuple:
	poll_client_info(self, client_id=ottdtype.MAX_UINT) -> tuple:
	poll_company_info(self, company_id=ottdtype.MAX_UINT) -> tuple:
	poll_company_economy(self, company_id=ottdtype.MAX_UINT) -> tuple:
	poll_company_stats(self, company_id=ottdtype.MAX_UINT) -> tuple:
	rcon_cmd(self, rcon_cmd) -> str:
	chat_all(self, message):
	chat_team(self, company_id, message):
	chat_client(self, client_id, message):
	chat_external(self, source, user, message, color = 0):
	request_date_updates(self, frequency = ottdtype.AdminUpdateFrequency.ADMIN_FREQUENCY_DAILY) -> bool:				# clamp Daily - anually
	request_client_info_updates(self, frequency = ottdtype.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:		# clamp Daily - automatic
	request_company_info_updates(self) -> bool:																			# Only Automatic
	request_company_economy_updates(self, frequency = ottdtype.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY) -> bool:	# clamp weekly - anually
	request_company_stats_updates(self, frequency = ottdtype.AdminUpdateFrequency.ADMIN_FREQUENCY_WEEKLY ) -> bool:		# clamp weekly - anually
	request_chat_updates(self, frequency = ottdtype.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
	request_console_updates(self, frequency = ottdtype.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
	request_cmd_names_updates(self, frequency = ottdtype.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
	request_cmd_logging_updates(self, frequency = ottdtype.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
	request_gamescript_updates(self, frequency = ottdtype.AdminUpdateFrequency.ADMIN_FREQUENCY_AUTOMATIC) -> bool:
	get_registered_updates(self):


## class RabbitMQ
	def __init__(self, server_ip, server_port) -> None:
	def create_queue_exchange(self):
	def clean_up(self):
	def control_queue_callback(self, ch, method, properties, body):
	def publish_message(self, key, message):
	def start_consuming(self):
	def register_msg_callback(self, callback, tag = "admin"):