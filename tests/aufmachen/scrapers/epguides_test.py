import unittest

import sys
sys.path.insert(0, '../../..')

from aufmachen.scrapers import epguides

class EpguidesTestCase(unittest.TestCase):
    
    def test_my_name_is_earl(self):
        earl_series = epguides.series.get('mynameisearl')
        self.assertEquals(earl_series['title'], u'My Name is Earl')
        self.assertEquals(len(earl_series['seasons']), 4)
        season_1 = earl_series['seasons'][0]
        self.assertEquals(season_1['number'], 1)
        self.assertEquals(len(season_1['episodes']), 24)
        s01e01 = season_1['episodes'][0]
        self.assertEquals(s01e01['epid'], 1)
        self.assertEquals(s01e01['number'], 1)
        self.assertEquals(s01e01['season'], 1)
        self.assertEquals(s01e01['title'], u'Pilot')
        self.assertEquals(s01e01['production_number'], u'1ALJ79')
        self.assertEquals(s01e01['air_date'], u'2005-09-20')
        
    def test_lost(self):
        lost_series = epguides.series.get('lost')
        self.assertEquals(lost_series['title'], u'Lost')
        self.assertEquals(len(lost_series['seasons']), 6)
        season_3 = lost_series['seasons'][2]
        self.assertEquals(season_3['number'], 3)
        self.assertEquals(len(season_3['episodes']), 23)
        s03e11 = season_3['episodes'][10]
        self.assertEquals(s03e11['epid'], 60)
        self.assertEquals(s03e11['number'], 11)
        self.assertEquals(s03e11['season'], 3)
        self.assertEquals(s03e11['title'], u'Enter 77')
        self.assertEquals(s03e11['production_number'], u'311')
        self.assertEquals(s03e11['air_date'], u'2007-03-07')
        
if __name__=='__main__':
    unittest.main()