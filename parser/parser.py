import math
import os
import logging
import pickle
import random
import requests
import time
from bs4 import BeautifulSoup
from twocaptcha import TwoCaptcha
from urllib.parse import urlencode, urljoin
from user_agent import generate_user_agent
from core.settings import (
    BASE_DIR,
    GOOGLE_SITE_KEY,
    RUCAPTCHA_API_KEY
)
from core.proxy import load_proxies
from helpers.parse_html import (
    ItemType,
    Tire,
    Disk,
    get_links_from_html,
    get_number_of_items,
    resolve_item_type,
    get_item_id,
    get_item_params_for_mmy_request,
    parse_tire,
    parse_disk
)


logger = logging.getLogger(__file__)


class Parser:
    """ Base class for parsing farpost.ru """

    def __init__(self, base_url: str, from_link: str = None):
        assert isinstance(base_url, str), '`base_url` parameter must be a str instance'

        self._base_url = base_url
        self._from_link = from_link  # Item to start parse
        self._session = requests.Session()
        self._user_agent: str = generate_user_agent(device_type=['smartphone', 'tablet'])
        self._proxies = load_proxies()  # All proxies
        self._proxy = self._proxies[0]  # Current proxy

        # Dictionary for further using with requests
        self._requests_proxies = {
            'http':
                f'socks5://{self._proxy.username}:{self._proxy.password}@{self._proxy.ip}:{self._proxy.port_socks5}',
            'https':
                f'socks5://{self._proxy.username}:{self._proxy.password}@{self._proxy.ip}:{self._proxy.port_socks5}'
        }

        # Headers to send while imitating a user behavior
        self._user_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
                      'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru',
            'sec-ch-ua-mobile': '?1',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'user-agent': self._user_agent,
            'referer': self._base_url
        }

        # Headers to send while imitating a js behavior
        self._script_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
                      'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru',
            'sec-ch-ua-mobile': '?1',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': self._user_agent
        }

        self._links = []  # Links to catalog items
        self._tires: list[Tire] = []  # Tires parsed
        self._disks: list[Disk] = []  # Disks parsed

    def _load_session_cookies(self) -> None:
        session_cookies_filename = os.path.join(BASE_DIR, f'tmp/{self._proxy.id}_cookies')

        if os.path.exists(session_cookies_filename):
            with open(session_cookies_filename, 'rb') as f:
                cookies = pickle.load(f)

            self._session.cookies.update(cookies)

    def _dump_session_cookies(self) -> None:
        session_cookies_filename = os.path.join(BASE_DIR, f'tmp/{self._proxy.id}_cookies')

        with open(session_cookies_filename, 'rb') as f:
            f.read()
            pickle.dump(self._session.cookies, f)

    def dump_tires(self) -> None:
        tires_filename = os.path.join(BASE_DIR, f'tmp/{self._proxy.id}_tires.xml')

        with open(tires_filename, 'w') as f:
            f.write(
                """<?xml version="1.0" encoding="UTF-8"?>
                    <products>
                """
            )

            for tire in self._tires:
                f.write(tire.to_xml())

            f.write('</products>')

    def dump_disks(self) -> None:
        disks_filename = os.path.join(BASE_DIR, f'tmp/{self._proxy.id}_disks.xml')

        with open(disks_filename, 'w') as f:
            f.write(
                """<?xml version="1.0" encoding="UTF-8"?>
                    <products>
                """
            )

            for disk in self._disks:
                f.write(disk.to_xml())

            f.write('</products>')

    def _solve_recaptcha_if_recaptcha(self, response: requests.Response) -> requests.Response:
        """ Solves recaptcha if it presents in the response """

        soup = BeautifulSoup(response.text, features='html.parser')

        try:
            hidden_s = soup.find('input', {'name': 's'}).get('value')
            hidden_t = soup.find('input', {'name': 't'}).get('value')

            logger.debug('Resolving Recaptcha...')
            solver = TwoCaptcha(RUCAPTCHA_API_KEY)

            try:
                result = solver.recaptcha(sitekey=GOOGLE_SITE_KEY, url=response.url)
            except Exception as e:
                logger.exception(e)
            else:
                self._user_headers['referer'] = response.url
                response = self._session.post(
                    url=response.url,
                    headers=self._user_headers,
                    data={
                        's': hidden_s,
                        't': hidden_t,
                        'g-recaptcha-response': result['code']
                    },
                    proxies=self._requests_proxies,
                    allow_redirects=True
                )
                return response
        except AttributeError:  # No recaptcha in the response
            return response

    def _request(self, url: str, is_script=False) -> requests.Response:
        """ Makes a request to farpost.ru document """

        headers = self._script_headers if is_script else self._user_headers

        logger.debug(
            f'url: {url} \n headers: {headers} \n proxies: {self._requests_proxies}'
        )

        try:
            response = self._session.get(
                url=url,
                proxies=self._requests_proxies,
                headers=headers
            )

            return self._solve_recaptcha_if_recaptcha(response)
        except requests.exceptions.ConnectTimeout:
            time.sleep(5)
            self._request(url, is_script)

    def _mmy_request(self, query_params: dict):
        """ Makes a request to /mmy.txt with query parameters """

        url = 'https://www.farpost.ru/mmy.txt?' + urlencode(query_params)
        self._request(url, is_script=True)

    def get_catalog_links(self):
        """ Returns all links in a catalog (base_url) """

        self._load_session_cookies()

        logger.debug(f'Requesting: {self._base_url}')

        # First user request for page in browser
        response = self._request(url=self._base_url)

        logger.debug(f'Response: {response.text}')

        # Extract links from html
        self._links.extend(
            get_links_from_html(response.text)
        )

        number_of_items, number_of_pages = get_number_of_items(response.text)
        logger.debug(f'Items: {number_of_items}, pages: {number_of_pages}')

        logger.debug('Scroll delay')

        # Scroll delay
        time.sleep(random.randint(15, 20))

        for i in range(2, number_of_pages + 1):
            url = self._base_url + f'?_lightweight=1&ajax=1&async=1&city=0&page={i}&status=actual'
            logger.debug(f'Requesting: {url}')

            response = self._request(url, is_script=True)

            logger.debug(f'Response: {response.text}')

            # Extract links from json
            self._links.extend(
                get_links_from_html(response.json()['feed'])
            )

            timestamp = int(time.time())

            logger.debug('Requesting mmy...')
            self._mmy_request(
                query_params={
                    'action': 'viewdir_ppc_good_show__in_0',
                    'keyName': '0__rel_0',
                    '_': timestamp
                }
            )

            time.sleep(1)

            logger.debug('Requesting mmy...')
            self._mmy_request(
                query_params={
                    'action': 'page_clicked',
                    'keyName': i,
                    '_': timestamp + 1
                }
            )

            self._script_headers['referer'] = self._base_url + f'?page={i}'

            logger.debug('Scroll delay')

            # Scroll delay
            time.sleep(random.randint(15, 20))

    def parse_catalog_items(self):
        """  """

        # If there is an item to start parse
        if self._from_link:
            from_item_index = self._links.index(self._from_link)
            links = self._links[from_item_index:]
        else:
            from_item_index = None
            links = self._links

        total_links = len(self._links)

        for i, link in enumerate(links, start=from_item_index - 1 if from_item_index else 0):
            item_page = math.ceil((i + 1) / 50)  # Number of page where current item located
            self._user_headers['referer'] = self._base_url + f'?page={item_page}'
            self._script_headers['referer'] = urljoin(self._base_url, link)

            logger.debug(f'Requesting: {i + 1} / {total_links} {link}')
            response = self._request('https://www.farpost.ru' + link)

            timestamp = int(time.time())
            item_id = get_item_id(link)
            item_type = resolve_item_type(response.text)

            logger.debug(f'Item id: {item_id}, item type: {item_type}, item page: {item_page}')

            query_params = {
                'action': 'viewdir_item_click',
                'briefType': 'inline',
                'searchPos': i + 1,
                'accuracy': 'exact',
                'bullId': item_id,
                '_': timestamp,
                **get_item_params_for_mmy_request(response.text)
            }
            self._mmy_request(query_params)

            time.sleep(1)
            self._mmy_request(
                query_params={
                    'action': 'viewbull_similar_block_bottom__exists',
                    'keyName': 'not_show',
                    '_': timestamp + 1
                }
            )

            time.sleep(1)
            self._mmy_request(
                query_params={
                    'action': 'viewbull_ask_button_is_visible',
                    '_': timestamp + 2
                }
            )

            match item_type:
                case ItemType.TIRE:
                    tire = parse_tire(response.text)
                    logger.debug(f'Parsed tire: {tire}')
                    self._tires.append(tire)

                case ItemType.DISK:
                    disk = parse_disk(response.text)
                    logger.debug(f'Parsed disk: {disk}')
                    self._disks.append(disk)
                case _:
                    logger.debug('Not a disk or tire.')

            if bool(random.getrandbits(1)):  # Random choice whether to scroll page to bottom
                # Scroll delay
                time.sleep(random.randint(1, 10))
                self._mmy_request(
                    query_params={
                        'action': 'viewbull_similar_block_bottom__show',
                        'keyName': 'not_show',
                        '_': int(time.time())
                    }
                )

            logging.debug('Delay after product watching.')
            # Delay after product watching
            time.sleep(random.randint(1, 10))
