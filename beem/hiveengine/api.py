import json
import requests


class HiveEngineAPI:
    def __init__(self, url="https://api.hive-engine.com/rpc/contracts"):
        self.url = url

    def call(self, method, params):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }

        r = requests.post(self.url, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()

        if "error" in data:
            raise Exception(data["error"])

        return data.get("result")

    def find(self, contract, table, query=None, limit=1000, offset=0, indexes=None):
        params = {
            "contract": contract,
            "table": table,
            "query": query or {},
            "limit": limit,
            "offset": offset
        }

        if indexes:
            params["indexes"] = indexes

        return self.call("find", params)

    def find_one(self, contract, table, query=None):
        result = self.find(contract, table, query=query, limit=1)
        return result[0] if result else None
