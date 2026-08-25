import re, functools, time
from pyopenttdadmin import Admin, AdminUpdateType, openttdpacket as p, Auth

import PlayerCompanyDB as PCDB




def init(host: str, admin_pass: str, admin_name: str = "admin", port: str = 3977, admin_version: str = "v1.0"):

    auth = Auth(name = admin_name, version = admin_version, password = admin_pass)
    admin = Admin(ip = host, port = port, auth = auth)

    rcon_buffer = []
    chat_cmd_registry = {}
    playerCoDB = PCDB.PlayerCompanyDatabase()


    def chat_command(name: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(admin, packet, *args, **kwargs):
                return func(admin, packet, *args, **kwargs)
            chat_cmd_registry[name.lower()] = wrapper
            return wrapper
        return decorator


    @chat_command("reset")
    def handle_reset(admin, packet, args):
        client_id = packet.id
        company_id = playerCoDB.get_client_company(client_id, None)

        if not company_id:
            admin.send_private("Something is wrong!!!", client_id)
            admin.send_private("Please try again in a minute.", client_id)
            admin.send_rcon("clients")
            return

        if company_id == PCDB.SPECTATOR_CO:
            admin.send_private("You need to be in a company to do this.!!!", client_id)
            return
        
        co_members = playerCoDB.get_company_clients(company_id)
        if len(co_members) > 1:
            admin.send_private("There are other players in the company.!!!", client_id)
            return
        
        admin.send_rcon(f'move {client_id} {PCDB.SPECTATOR_CO}')
        admin.send_rcon(f'reset_company {company_id}')


    @chat_command("help")
    def handle_help(admin, packet, args = None):
        admin.send_private(" ", packet.id)
        admin.send_private("========[ HELP MENU ]========", packet.id)

        admin.send_private("  !help  :: Show this help message", packet.id)
        admin.send_private("  !reset :: Delete current company", packet.id)
        admin.send_private("  !rules :: Show server rules", packet.id)
        admin.send_private("  !info  :: Show server tips", packet.id)

        admin.send_private("=============================", packet.id)
        admin.send_private(" ", packet.id)


    @chat_command("rules")
    def handle_rules(admin, packet, args = None):
        admin.send_private(" ", packet.id)
        admin.send_private("========[ RULES ]========", packet.id)

        admin.send_private(" 1. Respect other players.", packet.id)
        admin.send_private(" 2. Do not block other players.", packet.id)
        admin.send_private(" 3. Do not steal primary & secondary resources.", packet.id)
        admin.send_private(" 4. Towns are open for all.", packet.id)
        admin.send_private(" 5. Do not build city grids.", packet.id)
        admin.send_private(" 6. Please use only English in chat.", packet.id)

        admin.send_private("=========================", packet.id)
        admin.send_private(" ", packet.id)

    @chat_command("info")
    def handle_info(admin, packet, args = None):
        admin.send_private(" ", packet.id)
        admin.send_private("========[ INFO ]========", packet.id)
        admin.send_private(" ", packet.id)
        admin.send_private("Server resets in 31st December 2051", packet.id)
        admin.send_private("---------------------", packet.id)
        admin.send_private("Inactive companies are reset after 250 months (4 hours IRL).", packet.id)
        admin.send_private("---------------------", packet.id)
        admin.send_private("If going AFK for more than 4 hours, ", packet.id)
        admin.send_private("  add \"[AFK]\" at the end of the company name", packet.id)
        admin.send_private("  to extend company time by 4 hours.", packet.id)
        admin.send_private("---------------------", packet.id)
        admin.send_private("Use \"!help\" to view more commands.", packet.id)
        admin.send_private("---------------------", packet.id)
        admin.send_private(" ", packet.id)


    @admin.add_handler(p.ChatPacket)
    def chat_packet(admin: Admin, packet: p.ChatPacket):
        match = re.match(r'^!([a-zA-Z0-9_]+)(?:\s+(.*))?$', packet.message)
        if not match:
            return

        cmd_name = match.group(1).lower()
        cmd_args = match.group(2) or ""

        if cmd_name in chat_cmd_registry:
            chat_cmd_registry[cmd_name](admin, packet, args=cmd_args)
        else:
            admin.send_private(f'Invalid command: {cmd_name}', packet.id)


    @admin.add_handler(p.ClientJoinPacket)
    def client_join_packet(admin: Admin, packet: p.ClientJoinPacket):
        handle_info(admin, packet)


    @admin.add_handler(p.ClientQuitPacket)
    def client_quit_packet(admin: Admin, packet: p.ClientQuitPacket):
        playerCoDB.pop_client(packet.id)


    @admin.add_handler(p.ClientInfoPacket)
    @admin.add_handler(p.ClientUpdatePacket)
    def client_info_packet(admin: Admin, packet: p.ClientInfoPacket):
        playerCoDB.update_client(packet.id, int(packet.company_id) + 1)


    @admin.add_handler(p.RconPacket)
    def admin_rcon_packet_handler(admin: Admin, packet: p.RconPacket):
        rcon_buffer.append(packet.response)


    @admin.add_handler(p.RconEndPacket)
    def admin_rcon_end_handler(admin: Admin, packet: p.RconEndPacket):
        cmd = packet.command.strip()

        if cmd == "clients":
            pattern = r"Client #(?P<client_id>\d+)\s+name:\s*(?P<name>'.*?')\s+company:\s*(?P<company_id>\d+)\s+IP:\s*(?P<ip>\S+)"
            for rclient in rcon_buffer:
                match = re.search(pattern, rclient)
                if match:
                    data = match.groupdict()
                    playerCoDB.update_client(data['client_id'], data['company_id'])

        rcon_buffer.clear()


    @admin.add_handler(p.NewGamePacket)
    def admin_new_game_handler(admin: Admin, packet: p.NewGamePacket):
        print("New game started. Local state reset.")
        playerCoDB.clear()
        admin.socket.close()

    
    @admin.add_handler(p.ShutdownPacket)
    def admin_shutdown_handler(admin: Admin, packet: p.ShutdownPacket):
        print("Server is shutting down.")
        try:
            if hasattr(admin, 'socket') and admin.socket:
                admin.socket.close()
        except Exception:
            pass


    return admin



#======================================================================



if __name__ == "__main__":
    consecutive_failures = 0
    max_consecutive_failures = 3

    while True:
        connection_start_time = time.time()

        try:
            bot = init(host = "localhost", admin_pass = "12345678")
            bot.subscribe(AdminUpdateType.CLIENT_INFO)
            bot.subscribe(AdminUpdateType.CHAT)

            bot.send_rcon("clients")
            bot.run()
        except KeyboardInterrupt:
            print("\nCtrl+C received. Shutting down.")
            break
        except Exception as e:
            print(f"\nError: {e}")

        uptime = time.time() - connection_start_time
        consecutive_failures += -(consecutive_failures) if uptime > 30 else 1

        if consecutive_failures >= max_consecutive_failures:
            print(f"Error: Failed to connect. attempts: ({consecutive_failures}/{max_consecutive_failures})")
            print("Exiting!!!\n")
            break

        print("Attempting to reconnect.")

        time.sleep(5)


