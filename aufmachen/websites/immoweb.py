from random import choice
import string
import json
import re
from time import strptime, strftime

import sys
sys.path.append('../..')
from aufmachen.crawler import get_url, CRAWLERS, range_limit
from aufmachen.websites import BaseResource
from aufmachen.soupselect import select
from aufmachen.BeautifulSoup import BeautifulSoup, NavigableString

ESTATE_TYPE = ['']
ZIP_CODE = ''

KEY_ESTATE_TYPE = 'estate_type'
KEY_ZIP_CODE = 'zip_code'
KEY_ZIP_CODE2 = 'zip_code2'
KEY_PRICE_MIN = 'min_price'
KEY_PRICE_MAX = 'max_price'
KEY_BEDROOMS_MIN = 'min_bedrooms'
KEY_BEDROOMS_MAX = 'max_bedrooms'

ESTATE_TYPE_HOUSE = 'house'

IMMOWEB_KEY_MAP = {
    KEY_ESTATE_TYPE: 'XIDCATEGORIE',
    KEY_ZIP_CODE: 'XCODECOMMUNE1',
    KEY_PRICE_MIN: 'XPRICE1',
    KEY_PRICE_MAX: 'XPRICE2',
}

IMMOWEB_LIST_DEFAULTS = {
    'XTOOLBARMAP': 'Y',
    'XSHOW': '',
    'XTOOLBARCARTE': 'N',
    'MYCURRENT_SECTION': 'Buy',
    'XVENTELOCATION': '1',
    'XDISPLAY': 'estates',
    'XIDCATEGORIE': '1',
    'XPARIMG': 'on',
    'XPROVARRACTIVE': 'provincie%2Farrondiss%2E',
    'XPRICE1': '',
    'XPRICE2': '999999',
    'XDEVICE': 'EUR',
    'XMINROOM1': '',
    'XMINROOM2': '',
    'XSURFACEHABITABLETOTALE1': '',
    'XSURFACEHABITABLETOTALE2': '',
    'XSURFACETOTALETERRAIN1': '',
    'XSURFACETOTALETERRAIN2': '',
    'XZIPOPEN': 'Y',
    'XPAROPEN': 'N',
    'XIDREGIONXIDPROVINCEXIDARRONDISSEMENTBIS': '%20%2C%20%2C%20',
    'MAPCHANGED': '0',
    'XORDERBY1': 'datemodification',
    'XCODECOMMUNELIBRE': '',
    'XCODECOMMUNE1': '',
    'XADKEY': '000004',
}

IMMOWEB_ESTATE_TYPE_MAP = {
    ESTATE_TYPE_HOUSE: 1,
    'Huis': 'house'
}

IMMOWEB_VALUE_MAP = {
    (KEY_ESTATE_TYPE, 'house'): '1'
}


import urllib
from copy import copy
def immoweb_retrieve(url, data):
    range_limit()
    print "iGET", url
    f = iPhoneURLOpener().open(url, data)
    html = f.read().decode('utf-8', 'ignore')
    return f.getcode(), html

CRAWLERS['immoweb_crawler'] = immoweb_retrieve

IMMOWEB_IPHONE_URL = 'http://www.immoweb.be/nl/iphone.cfc'

RANDOM_IPHONE_ID = ''.join([choice(string.hexdigits) for i in range(40)]).lower()

DEFAULT_FORM_DATA = {
    'iPhone': RANDOM_IPHONE_ID,
    'ClientSource': '',
    'LoggedIdClient': '0',
}

class iPhoneURLOpener(urllib.FancyURLopener):
    version = 'Immoweb/1.1 CFNetwork/485.13.9 Darwin/11.0.0'

ADDRESS_RE = re.compile('(.*?)\s*(\d{4})\s+-\s+(.*)')

def find_string(regex, s):
    """Find a string using a given regular expression. 
    If the string cannot be found, returns None.
    The regex should contain one matching group, 
    as only the result of the first group is returned.

    s - The string to search.
    regex - A string containing the regular expression.
    
    Returns a unicode string or None.
    """
    m = re.search(regex, s)
    if m is None:
        print '=ERR= Could not find %s in %s' % (regex, s)
        return None
    return m.groups()[0]
    
def find_number(regex, s):
    """Find a number using a given regular expression.
    If the string cannot be found, returns None.
    The regex should contain one matching group, 
    as only the result of the first group is returned.
    The group should only contain numeric characters ([0-9]+).
    
    s - The string to search.
    regex - A string containing the regular expression.
    
    Returns an integer or None.
    """
    result = find_string(regex, s)
    if result is None:
        return None
    return int(result)
    
def parse_first_number(s):
    """Parse the first number in the string we encounter.
    
    s - The string to parse.
    
        parse_first_number('123')
        >>> 123
        parse_first_number('   12 meters')
        >>> 12
        parse_first_number('area: 156 meters')
        >>> 156
        parse_first_number(' 1 2 3')
        >> 1
        parse_first_number('    ')
        >> None

    Returns an integer or None if no number could be found.
    """
    m = re.match('\s*.*?(\d+)', s)
    if m is None: return None
    return int(m.groups(1)[0])

def clean_text(s):
    """Removes all cruft from the text."""
    SPACES_RE = re.compile(r'\s+')
    SPECIAL_CHARS_RE = re.compile(r'[^\w\s\.\-\(\)]')
    s = SPACES_RE.sub(' ', s)
    s = s.strip()
    s = SPECIAL_CHARS_RE.sub('', s)
    return s

def parse_immoweb_link(url):
    """Parses an Immoweb estate detail URL and returns the Immoweb estate id.

    Returns a string with the Immoweb estate id.
    """
    IMMOWEB_ID_RE = re.compile(r'.*?IdBien=([0-9]+).*?')
    return IMMOWEB_ID_RE.match(url).groups()[0]

def parse_number(d, key, regex, s):
    """Find a number using a given regular expression.
    If the number is found, sets it under the key in the given dictionary.
    
    d - The dictionary that will contain the data.
    key - The key into the dictionary.
    regex - A string containing the regular expression.
    s - The string to search.
    """
    result = find_number(regex, s)
    if result is not None:
        d[key] = result
    
def parse_zip_code(s):
    NUMBERS_RE = re.compile(r'.*?([0-9]+).*?')
    s = clean_text(s)
    return NUMBERS_RE.match(s).groups()[0]

def parse_estate_type(s):
    s = clean_text(s).lower()
    if s.startswith('huis'):
        return 'house'
    else:
        return 'other'

def parse_city(s):
    AFTER_ZIP_CODE_RE = re.compile(r'[0-9]+\s+(.*)$')
    s = clean_text(s)
    return AFTER_ZIP_CODE_RE.match(s).groups()[0]
    
def parse_price(s):
    try:
        return int(''.join(re.findall('[0-9]', s)))
    except ValueError:
        return None

def deep_contents(node):
    if isinstance(node, NavigableString):
        return node.string
    #elif isinstance(node, list):
    #    return u''.join(deep_contents(child) for child in node)
    else:
        return u''.join([deep_contents(child) for child in node])
        
def conditional_set(d, k, v):
    """Sets the key to value in the dictionary if the value is not None.
    
    d - The dictionary.
    k - The key to set.
    v - The value to set.
    """
    if v is not None:
        d[k] = v
    
class Estates(BaseResource):
    
    def list_url(self, **kwargs):
        from copy import copy

        immoweb_attributes = copy(IMMOWEB_LIST_DEFAULTS)
        for k, v in kwargs.items():
            immoweb_key = IMMOWEB_KEY_MAP[k]
            immoweb_value = IMMOWEB_VALUE_MAP.get((immoweb_key, v), v)
            immoweb_attributes[immoweb_key] = immoweb_value
        return 'http://www.immoweb.be/nl/Buy.Results.cfm?' + \
               '&'.join(['%s=%s' % (key, value) \
               for key, value in immoweb_attributes.items()])
        
    def parse_list(self, html):
        soup = BeautifulSoup(html)
        immoweb_ids = []
        estates = []
        estates_table_rows = select(soup, '.result-liste tr')
        for estate_row in estates_table_rows[1:]:
            estate = {}
            estate_row_cells = select(estate_row, 'td')
            # Cell 0: price
            estate_price_cell = estate_row_cells[0]
            conditional_set(estate, 'price', parse_price(estate_price_cell.string))
            # Cell 1: type + link
            estate_link = select(estate_row, 'a')[0]['href']
            estate['id'] = parse_immoweb_link(estate_link)
            estate['estate_type'] = parse_estate_type(deep_contents(estate_row_cells[1]))
            # Cell 2: area
            conditional_set(estate, 'area', parse_first_number(estate_row_cells[2].string))
            # Cell 3: bedrooms
            conditional_set(estate, 'bedrooms', parse_first_number(estate_row_cells[3].string))
            # Cell 4: zip_code + city
            estate_city_cell = estate_row_cells[4]
            estate['zip_code'] = parse_zip_code(estate_city_cell.string)
            estate['city'] = parse_city(estate_city_cell.string)
            estates.append(estate)
        return estates
        
    def get_detail_html(self, id, cached=True):
        form_data = copy(DEFAULT_FORM_DATA)
        form_data['Method'] = 'GetEstate'
        form_data['IdBien'] = str(id)
        return get_url(IMMOWEB_IPHONE_URL, data=urllib.urlencode(form_data), 
            crawler='immoweb_crawler', cached=cached, cache_key=id)

    def parse_detail(self, id, html):
        # The HTML is actually JSON.
        raw_data = json.loads(html)
        
        estate = {}
        
        def _parse(key, fn, *args, **kwargs):
            result = fn(*args, **kwargs)
            if result is not None:
                estate[key] = result
        
        estate['id'] = id
        
        # XIPHONEARRAY_MAININFO contains the title, pictures, price, area / bedrooms and address.
        raw_title = raw_data['XIPHONEARRAY_MAININFO'][0]
        raw_pictures = raw_data['XIPHONEARRAY_MAININFO'][1]
        raw_price = raw_data['XIPHONEARRAY_MAININFO'][2]
        raw_location_description = raw_data['XIPHONEARRAY_MAININFO'][3]
        raw_address = raw_data['XIPHONEARRAY_MAININFO'][5]

        if 'Huis' in raw_data['XIPHONEARRAY_MAININFO'][0]:
            estate['estate_type'] = 'house'
        else:
            estate['estate_type'] = 'other'

        estate['price'] = parse_price(raw_price)
        _parse('bedrooms', find_number, r'([0-9]+) slaapkamers', raw_location_description)
        _parse('area', find_number, r'bewoonbare oppervlakte: ([0-9]+)', raw_location_description)

        raw_address_lines = raw_address.splitlines()
        
        if len(raw_address_lines) == 1:
            city_line = raw_address_lines[0]
        elif len(raw_address_lines) == 2:
            estate['address'] = raw_address_lines[0].strip()
            city_line = raw_address_lines[1]
        else:
            print 'Do not know how to handle address:', raw_address
        estate['zip_code'], estate['city'] = city_line.split(' - ')

        raw_title_lines = raw_title.splitlines()
        if len(raw_title_lines) >= 2:
            estate['title'] = raw_title_lines[0]
        
        # XIPHONEARRAY_DESCRIPTION contains the full description. Every line is an element in the list.
        raw_description = raw_data['XIPHONEARRAY_DESCRIPTION'][0]
        estate['description'] = '\n'.join(raw_description.splitlines())

        return estate

estates = Estates()

if __name__=='__main__':
    from pprint import pprint
    pprint(estates.get('3224154'))