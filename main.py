import logging
from parser import Parser


logger = logging.getLogger(__file__)


if __name__ == '__main__':
    parser = Parser(base_url='https://www.farpost.ru/user/VLtires/auto/wheel/')
    parser.get_catalog_links()

    try:
        parser.parse_catalog_items()
    except Exception as e:
        logger.exception(e)

    parser.dump_disks()
    parser.dump_tires()
