import json
import math
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class ItemType(Enum):
    TIRE = 0,
    DISK = 1


@dataclass
class Tire:
    title: str
    price: str
    the_number_of_tires_in_an_indivisible_set: str
    total_sets: str
    tire_year: int
    tread: str
    product_condition: str
    landing_diameter: str
    profile_width: str
    profile_height: str
    frame: str
    availability_of_goods: str
    tire_type: str

    def __dict__(self):
        return {
            'title': self.title,
            'price': self.price,
            'theNumberOfTiresInAnIndivisibleSet': self.the_number_of_tires_in_an_indivisible_set,
            'totalSets': self.total_sets,
            'tireYear': self.tire_year,
            'tread': self.tread,
            'productCondition': self.product_condition,
            'landingDiameter': self.landing_diameter,
            'profileWidth': self.profile_width,
            'profileHeight': self.profile_height,
            'frame': self.frame,
            'availabilityOfGoods': self.availability_of_goods,
            'tireType': self.tire_type
        }

    @classmethod
    def from_dict(cls, _dict: dict):
        return cls(
            title=_dict['title'],
            price=_dict['price'],
            the_number_of_tires_in_an_indivisible_set=_dict['theNumberOfTiresInAnIndivisibleSet'],
            total_sets=_dict['totalSets'],
            tire_year=_dict['tireYear'],
            tread=_dict['tread'],
            product_condition=_dict['productCondition'],
            landing_diameter=_dict['landingDiameter'],
            profile_width=_dict['profileWidth'],
            profile_height=_dict['profileHeight'],
            frame=_dict['frame'],
            availability_of_goods=_dict['availabilityOfGoods'],
            tire_type=_dict['tireType']
        )

    def to_xml(self):
        return f"""<Tire>
            <title>{self.title}</title>
            <price>{self.price}</price>
            <theNumberOfTiresInAnIndivisibleSet>{self.the_number_of_tires_in_an_indivisible_set}</theNumberOfTiresInAnIndivisibleSet>
            <totalSets>{self.total_sets}</totalSets>
            <tireYear>{self.tire_year}</tireYear>
            <tread>{self.tread}</tread>
            <productCondition>{self.product_condition}</productCondition>
            <landingDiameter>{self.landing_diameter}</landingDiameter>
            <profileWidth>{self.profile_width}</profileWidth>
            <profileHeight>{self.profile_height}</profileHeight>
            <frame>{self.frame}</frame>
            <availabilityOfGoods>{self.availability_of_goods}</availabilityOfGoods>
            <tireType>{self.tire_type}</tireType>
        </Tire>"""


@dataclass
class Disk:
    title: str
    price: str
    number_of_discs_included: str
    number_of_sets: str
    product_condition: str
    diameter: str
    disc_width: str
    departure_ET: str
    drilling_PCD: str
    type_of: str
    CH_diameter_DIA: str
    product_availability: str

    def __dict__(self):
        return {
            'title': self.title,
            'price': self.price,
            'NumberOfDiscsIncluded': self.number_of_discs_included,
            'NumberOfSets': self.number_of_sets,
            'ProductCondition': self.product_condition,
            'Diameter': self.diameter,
            'DiscWidth': self.disc_width,
            'DepartureET': self.departure_ET,
            'DrillingPCD': self.drilling_PCD,
            'TypeOf': self.type_of,
            'CHDiameterDIA': self.CH_diameter_DIA,
            'ProductAvailability': self.product_availability
        }

    @classmethod
    def from_dict(cls, _dict: dict):
        return cls(
            title=_dict['title'],
            price=_dict['price'],
            number_of_discs_included=_dict['NumberOfDiscsIncluded'],
            number_of_sets=_dict['NumberOfSets'],
            product_condition=_dict['ProductCondition'],
            diameter=_dict['Diameter'],
            disc_width=_dict['DiscWidth'],
            departure_ET=_dict['DepartureET'],
            drilling_PCD=_dict['DrillingPCD'],
            type_of=_dict['TypeOf'],
            CH_diameter_DIA=_dict['CHDiameterDIA'],
            product_availability=_dict['ProductAvailability']
        )

    def to_xml(self):
        return f"""<Disk>
            <title>{self.title}</title>
            <price>{self.price}</price>
            <NumberOfDiscsIncluded>{self.number_of_discs_included}</NumberOfDiscsIncluded>
            <NumberOfSets>{self.number_of_sets}</NumberOfSets>
            <ProductCondition>{self.product_condition}</ProductCondition>
            <Diameter>{self.diameter}</Diameter>
            <DiscWidth>{self.disc_width}</DiscWidth>
            <DepartureET>{self.departure_ET}</DepartureET>
            <DrillingPCD>{self.drilling_PCD}</DrillingPCD>
            <TypeOf>{self.type_of}</TypeOf>
            <CHDiameterDIA>{self.CH_diameter_DIA}</CHDiameterDIA>
            <ProductAvailability>{self.product_availability}</ProductAvailability>
        </Disk>"""


def get_links_from_html(content_to_parse: str) -> list[str]:
    """ Returns links to products """

    soup = BeautifulSoup(content_to_parse, features='html.parser')

    links = []

    for link in soup.find_all('a', class_='bull-item__self-link'):
        links.append(
            link.get('href')
        )

    return links


def get_number_of_items(content_to_parse: str) -> tuple[int, int]:
    """ Returns a total number of items and number of pages """

    soup = BeautifulSoup(content_to_parse, features='html.parser')
    span = soup.find('span', {'id': 'itemsCount_placeholder'})

    number_of_items = int(span.get('data-count'))
    return number_of_items, math.ceil(number_of_items / 50)


def resolve_item_type(content_to_parse: str) -> ItemType | None:
    """ Returns the type of item """

    soup = BeautifulSoup(content_to_parse, features='html.parser')
    div = soup.find('div', {'id': 'breadcrumbs'})

    if re.search(r'\nДиски\n', div.text):
        return ItemType.DISK
    elif re.search(r'\nШины\n', div.text):
        return ItemType.TIRE
    else:
        return


def get_item_id(link: str) -> str:
    """ Returns the id of item from item link """

    result = re.search(r'\d+.html', link)

    return result[0][:-5]  # Return first match without .html


def get_item_params_for_mmy_request(content_to_parse: str) -> dict:
    """ Returns item parameters from <script> for sending them to mmy.txt """

    result = re.split(r'Number\(\d+\), ', content_to_parse)
    result = re.split(r'\);', result[1])

    return json.loads(result[0])


def _process_parsed_string(string: str | None) -> str | None:
    """ Removes extra symbols from str """

    if string is None:
        return

    return string.replace('\n', '').replace('\t', '').replace('\xa0', '')


def _get_integer_from_string(string: str) -> int:
    """ Returns a string contains only integers from original string """

    return int(re.search(r'\d+', string).group())


def parse_tire(content_to_parse: str) -> Tire:
    """ Returns Tire dataclass after html parsing """

    soup = BeautifulSoup(content_to_parse, features='html.parser')

    title = soup.find('span', {'data-field': 'subject'}).text

    try:
        price_for_set = soup.find('span', {'data-field': 'price'}).get('data-bulletin-price')
    except AttributeError:
        price_for_set = None

    try:
        the_number_of_tires_in_an_indivisible_set = soup.find('span', {'data-field': 'inSetQuantity'}).text
    except AttributeError:
        the_number_of_tires_in_an_indivisible_set = None

    if price_for_set and the_number_of_tires_in_an_indivisible_set:
        price = str(int(price_for_set) / _get_integer_from_string(the_number_of_tires_in_an_indivisible_set))
    else:
        price = price_for_set

    total_sets = soup.find('span', {'data-field': 'quantity'}).text

    try:
        tire_year = soup.find('span', {'data-field': 'year'}).text
    except AttributeError:
        tire_year = None

    tread = soup.find('span', {'data-field': 'wheelSeason'}).text
    product_condition = soup.find('span', {'data-field': 'condition'}).text

    marking = soup.find_all('span', {'data-field': 'marking'})
    landing_diameter = marking[1].text
    profile_width = marking[2].text
    profile_height = marking[3].text
    frame = marking[4].text

    availability_of_goods = soup.find('span', {'data-field': 'goodPresentState'}).text
    tire_type = soup.find('span', {'data-field': 'predestination'}).text

    return Tire(
        title=_process_parsed_string(title),
        price=price,
        the_number_of_tires_in_an_indivisible_set=_process_parsed_string(the_number_of_tires_in_an_indivisible_set),
        total_sets=_process_parsed_string(total_sets),
        tire_year=_process_parsed_string(tire_year),
        tread=_process_parsed_string(tread),
        product_condition=_process_parsed_string(product_condition),
        landing_diameter=_process_parsed_string(landing_diameter),
        profile_width=_process_parsed_string(profile_width),
        profile_height=_process_parsed_string(profile_height),
        frame=_process_parsed_string(frame),
        availability_of_goods=_process_parsed_string(availability_of_goods),
        tire_type=_process_parsed_string(tire_type)
    )


def parse_disk(content_to_parse: str) -> Disk:
    """ Returns Disk dataclass after html parsing """

    soup = BeautifulSoup(content_to_parse, features='html.parser')

    title = soup.find('span', {'data-field': 'subject'}).text
    price_for_set = soup.find('span', {'data-field': 'price'}).get('data-bulletin-price')
    number_of_discs_included = soup.find('span', {'data-field': 'inSetQuantity'}).text

    price = str(int(price_for_set) / _get_integer_from_string(number_of_discs_included))

    number_of_sets = soup.find('span', {'data-field': 'quantity'}).text

    try:
        product_condition = soup.find('span', {'data-field': 'condition'}).text
    except AttributeError:
        product_condition = None
        
    diameter = soup.find('span', {'data-field': 'wheelDiameter'}).text

    try:
        disk_parameters = soup.find('div', {'data-field': 'discParameters'}).select('div.value')
    except AttributeError:
        disk_parameters = None

    try:
        disc_width = disk_parameters[0].text
    except (IndexError, TypeError):
        disc_width = None

    try:
        departure_ET = disk_parameters[1].text
    except (IndexError, TypeError):
        departure_ET = None

    drilling_PCD = soup.find('span', {'data-field': 'wheelPcd'}).text

    try:
        type_of = soup.find('span', {'data-field': 'diskType'}).text
    except AttributeError:
        type_of = None

    try:
        CH_diameter_DIA = soup.find('span', {'data-field': 'diskHoleDiameter'}).text
    except AttributeError:
        CH_diameter_DIA = None

    try:
        product_availability = soup.find('span', {'data-field': 'goodPresentState'}).text
    except AttributeError:
        product_availability = None

    return Disk(
        title=_process_parsed_string(title),
        price=price,
        number_of_discs_included=_process_parsed_string(number_of_discs_included),
        number_of_sets=_process_parsed_string(number_of_sets),
        product_condition=_process_parsed_string(product_condition),
        diameter=_process_parsed_string(diameter),
        disc_width=_process_parsed_string(disc_width),
        departure_ET=_process_parsed_string(departure_ET),
        drilling_PCD=_process_parsed_string(drilling_PCD),
        type_of=_process_parsed_string(type_of),
        CH_diameter_DIA=_process_parsed_string(CH_diameter_DIA),
        product_availability=_process_parsed_string(product_availability)
    )
