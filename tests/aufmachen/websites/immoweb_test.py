# -*- coding: utf-8 -*-

import os
import sys
import unittest

sys.path.insert(0, '../../..')

# Note that we need mock data, since the data on Immoweb will change rapidly.
from aufmachen import crawler
crawler.CACHE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../mocks/immoweb')
# If the data is not in the cache directory, something's wrong. Bail out.
crawler.FAIL_IF_NOT_CACHED = False

from aufmachen.websites import immoweb

class ImmowebTestCase(unittest.TestCase):
    
    def assert_estate(self, estate, detailed):
        self.assertEquals(estate['id'], '3154711')
        if detailed:
            self.assertEquals(estate['address'], u'Rue de la Gouttière, 29')
            self.assertTrue('huis van 17e eeuw spaanse stijl', estate['description'])
        self.assertEquals(estate['estate_type'], 'house')
        self.assertEquals(estate['price'], 310000)
        self.assertEquals(estate['area'], 156)
        self.assertEquals(estate['bedrooms'], 4)
        self.assertEquals(estate['zip_code'], '1000')
        self.assertEquals(estate['city'].lower(), 'bruxelles')
        
    def test_estates_list(self):
        estates = immoweb.estates.list(zip_code=1000, max_price=450000)
        self.assertEquals(len(estates), 48)
        self.assert_estate(estates[3], detailed=False)
        
    def test_estates_detail(self):
        estate = immoweb.estates.get('3154711')
        self.assert_estate(estate, detailed=True)
        
if __name__=='__main__':
    unittest.main()