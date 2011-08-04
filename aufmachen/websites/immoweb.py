import re
from time import strptime, strftime

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

# only new:
# 'XNEUF': 'U',

IMMOWEB_ESTATE_TYPE_MAP = {
    ESTATE_TYPE_HOUSE: 1,
    'Huis': 'house'
}

IMMOWEB_VALUE_MAP = {
    (KEY_ESTATE_TYPE, 'house'): '1'
}

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

def parse_price(s):
    PRICE_RE = re.compile(r'[^0-9]')
    try:
        return int(PRICE_RE.sub('', s))
    except ValueError:
        return None

def parse_immoweb_link(url):
    """Parses an Immoweb estate detail URL and returns the Immoweb estate id.

    Returns a string with the Immoweb estate id.
    """
    IMMOWEB_ID_RE = re.compile(r'.*?IdBien=([0-9]+).*?')
    return IMMOWEB_ID_RE.match(url).groups()[0]

def clean_text(s):
    """Removes all cruft from the text."""
    SPACES_RE = re.compile(r'\s+')
    SPECIAL_CHARS_RE = re.compile(r'[^\w\s\.\-\(\)]')
    s = SPACES_RE.sub(' ', s)
    s = s.strip()
    s = SPECIAL_CHARS_RE.sub('', s)
    return s

def parse_estate_type(s):
    s = clean_text(s).lower()
    if s.startswith('huis'):
        return 'house'
    else:
        return 'other'

def parse_zip_code(s):
    NUMBERS_RE = re.compile(r'.*?([0-9]+).*?')
    s = clean_text(s)
    return NUMBERS_RE.match(s).groups()[0]

def parse_city(s):
    AFTER_ZIP_CODE_RE = re.compile(r'[0-9]+\s+(.*)$')
    s = clean_text(s)
    return AFTER_ZIP_CODE_RE.match(s).groups()[0]
    
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
    
NUMBERS = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')

class Estates(BaseResource):
    
    # Scraping by making a simple page request is not possible. 
    # Immoweb inserts the address into the page using a script tag.
    # The workaround is to use PhantomJS to render the page, 
    # including all script content. We then extract the innerHTML 
    # from the body, which gives us the fully evaluated page.
    crawler = 'phantomjs'
    
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
            estate['price'] = parse_price(estate_price_cell.string)
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

    def detail_url(self, id):
        return 'http://www.immoweb.be/nl/global.Estate.cfm?IdBien=%s' % id
        
    def parse_detail(self, id, html):
        soup = BeautifulSoup(html)
        estate = {}
        estate['id'] = id

        # Estate type
        if 'Huis' in deep_contents(select(soup, 'h1')):
            estate['estate_type'] = 'house'
        else:
            estate['estate_type'] = 'other'

        # Price
        estate['price'] = parse_price(select(soup, '.price')[0].string)
        
        # Bedrooms / Area
        estate['bedrooms'] = parse_first_number(select(soup, '.locationdescription li')[0].string)
        estate['area'] = parse_first_number(select(soup, '.locationdescription li')[1].string)
        
        # Address: '<li>Hendrik<font color="#e7ebf7">b</font>Geertstraat<font color="#e7ebf7">s</font>18</li>'
        address = select(soup, '.locationinfo li')
        # Sometimes the address is missing. The first line is then the zip_code / city line.
        street_contents = address[0].contents
        if not street_contents[0].startswith(NUMBERS):
            # Only keep the unicode parts (not the tags)
            street_parts = [s for s in street_contents if isinstance(s, unicode)]
            estate['address'] = ' '.join(street_parts)
            city_contents = address[1].contents
        else:
            city_contents = address[0].contents
            # Next line: zip code - city: '<li>2900<font color="#e7ebf7">&amp;</font>-<font color="#e7ebf7">c</font>Schoten</li>'
        estate['zip_code'] = city_contents[0]
        estate['city'] = city_contents[4]
        # Description
        # Title: '<h2>Volledig gerenoveerde woning met garage en diepe tuin</h2>'
        title_tag = soup.find('h2')
        # Immoweb sometimes uses an <iframe> to hide the contents. Don't try to parse any further if we can't find the title.
        if title_tag is not None:
            estate['title'] = clean_text(soup.find('h2').contents[0])
            # Description is the element of same parent the h2 is in.
            # It is after the <br> tag.
            estate['description'] = soup.find('h2').parent.find('br').next.strip()
        return estate

estates = Estates()