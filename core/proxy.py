import os
import csv
from typing import NamedTuple, Generator
from .settings import BASE_DIR


class Proxy(NamedTuple):
    id: str
    ip: str
    port_http: str
    port_socks5: str
    username: str
    password: str
    internal_ip: str


def load_proxies() -> tuple[Proxy]:
    filename = os.path.join(BASE_DIR, 'input/proxies.csv')
    proxies = []
    proxies_ids = []

    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=';')

        next(reader)  # Skip title line
        for row in reader:
            proxies.append(Proxy(*row))
            proxies_ids.append(row[0])

    assert len(proxies_ids) == len(set(proxies_ids)), 'Proxies in input/proxies.csv must have a unique ids'

    return tuple(proxies)
