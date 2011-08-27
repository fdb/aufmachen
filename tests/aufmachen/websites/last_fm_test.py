import os
import sys
import unittest

sys.path.insert(0, '../../..')

# Note that we need mock data, since the data on Immoweb will change rapidly.
from aufmachen import crawler
crawler.CACHE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../mocks/last_fm')
# If the data is not in the cache directory, something's wrong. Bail out.
crawler.FAIL_IF_NOT_CACHED = True

from aufmachen.websites import last_fm

class EpguidesTestCase(unittest.TestCase):
    
    def test_alter_ego_why_not(self):
        why_not_song = last_fm.song.get(['Alter Ego', 'Why Not'])
        self.assertEquals(why_not_song['artist'], u'Alter Ego')
        self.assertEquals(why_not_song['title'], u'Why Not')
        tags = why_not_song['tags']
        self.assertEquals(len(tags), 11)
        self.assertEquals(tags[0], '214 electronic')
        self.assertEquals(tags[4], 'electronic')
        
if __name__=='__main__':
    unittest.main()