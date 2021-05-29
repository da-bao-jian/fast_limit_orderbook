from typing import Dict, Tuple

class _Symbols:
    def __init__(self):
        self.data = {}

    def clear(self):
        self.data = {}

    def set(self, exchange: str, normalized: dict, exchange_info: dict):
        self.data[exchange] = {}
        self.data[exchange]['normalized'] = normalized
        self.data[exchange]['info'] = exchange_info
        breakpoint()

    def get(self, exchange: str) -> Tuple[Dict, Dict]:
        return self.data[exchange]['normalized'], self.data[exchange]['info']

    def populated(self, exchange: str) -> bool:
        return exchange in self.data


Symbols = _Symbols()
