from parser import Parser


if __name__ == '__main__':
    parser = Parser(base_url='https://www.farpost.ru/user/VLtires/auto/wheel/')
    parser.get_catalog_links()
    parser.parse_catalog_items()
    parser.dump_disks()
    parser.dump_tires()
