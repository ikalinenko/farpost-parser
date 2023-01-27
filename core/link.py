import os
import csv
from typing import NamedTuple
from .settings import BASE_DIR


class Link(NamedTuple):
    id: str
    url: str
    from_item: str | None


def load_links() -> tuple[Link]:
    filename = os.path.join(BASE_DIR, 'input/links.csv')
    links = []
    links_ids = []

    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=';')

        next(reader)  # Skip title line
        for row in reader:
            row[2] = row[2] if row[2] else None  # from_item=None if it is an empty string
            links.append(Link(*row))
            links_ids.append(row[0])

    assert len(links_ids) == len(set(links_ids)), 'Links in input/links.csv must have a unique ids'

    return tuple(links)
