from collections import defaultdict


SPECTATOR_CO : int = 255


class PlayerCompanyDatabase:
    def __init__(self):
        self._clients = {}
        self._companies = defaultdict(set)


    def update_client(self, client_id: int, company_id: int = SPECTATOR_CO) -> None:
        client_id = int(client_id)
        company_id = int(company_id)
        if client_id in self._clients:
            self.pop_client(client_id)

        self._clients[client_id] = company_id
        self._companies[company_id].add(client_id)


    def update_company(self, company_id: int, client_ids: list = [int]):
        if client_ids is None:
            client_ids = []
        
        for client_id in client_ids:
            self.add_client(client_id, company_id)


    def pop_client(self, client_id: int) -> None:
        if client_id not in self._clients:
            return

        company_id = self._clients.pop(client_id, None)
        if not company_id:
            raise ValueError("Client found with unregistered company mapping.")

        if company_id not in self._companies:
            raise ValueError("Client company not found in company db.")

        self._companies[company_id].discard(client_id)
        

    def pop_company(self, company_id: int, force: bool = False) -> bool:
        if company_id not in self._companies:
            return True

        clients = self._companies.get(company_id, set())
        if not force and len(clients) > 0:
            return False

        for client in list(clients):
            self._clients.pop(client, None)

        self._companies.pop(company_id, None)
        return True

    
    def get_client_company(self, client_id: int, default_value: int = None) -> int:
        return self._clients.get(client_id, default_value)


    def get_company_clients(self, company_id: int, default_value:set = set()) -> int:
        return self._companies.get(company_id, default_value)
    
        
    def clear(self) -> None:
        self._clients.clear()
        self._companies.clear()
        

    def __str__(self):
        return "ci: " + str(self._clients) + "\nco: " + str(self._companies) + "\n"
