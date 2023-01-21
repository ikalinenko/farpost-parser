import os
import csv
from typing import NamedTuple
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
    filename = os.path.join(BASE_DIR, 'files/proxies.csv')
    proxies = []

    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=';')

        next(reader)  # Skip title line
        for row in reader:
            proxies.append(Proxy(*row))

    return tuple(proxies)
