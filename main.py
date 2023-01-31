import argparse
import logging
import sys
from multiprocessing import Process
from core.proxy import Proxy, load_proxies
from core.link import Link, load_links
from parser import Parser


logger = logging.getLogger(__file__)


PROXIES = load_proxies()
LINKS = load_links()


def run_parser(link_id: str, proxy_id: str):
    """
        Starts a single parser for link with id=link_id from input/links.csv
        using proxy with id=proxy_id from input/proxies.csv
    """

    # Check link_id parameter
    filtered: list[Link] = list(filter(lambda link: link.id == link_id, LINKS))

    assert len(filtered) == 1, f'Link with id={link_id} does not exist in input/links.csv'
    link = filtered[0]

    # Check proxy_id parameter
    filtered: list[Proxy] = list(filter(lambda proxy: proxy.id == proxy_id, PROXIES))

    assert len(filtered) == 1, f'Proxy with id={link_id} does not exist in input/proxies.csv'
    proxy = filtered[0]

    # Run parser
    with Parser(_id=link_id,
                base_url=link.url,
                from_link=link.from_item,
                proxy=proxy) as parser:
        parser.run()


def run_parsers():
    """ Starts all parsers for each link from input/links.csv """

    assert len(PROXIES) >= len(LINKS), 'Number of proxies in input/proxies.csv ' \
                                       'must be more or equal than number of links in input/links.csv'

    processes = []
    for link, proxy in zip(LINKS, PROXIES):
        process = Process(target=run_parser, args=(link.id, proxy.id))
        processes.append(process)
        process.start()

    # Waiting for each process to complete
    for process in processes:
        process.join()


def main():
    """ Parser entrypoint """
    args = sys.argv[1:]

    # Parse arguments
    parser = argparse.ArgumentParser(description='Welcome to FarPost.ru parser')
    parser.add_argument('--link-id', type=str, help='Catalog link id to parse (id from input/links.csv)')
    parser.add_argument('--proxy-id', type=str, help='Proxy id to use (id from input/proxies.csv)')
    namespace = parser.parse_args(args)

    # Verify arguments
    if namespace.link_id and namespace.proxy_id:
        run_parser(link_id=namespace.link_id, proxy_id=namespace.proxy_id)
    elif not namespace.link_id and not namespace.proxy_id:
        run_parsers()
    else:
        print(f'You need either to specify --link-id and --proxy-id parameters or do not specify both', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
