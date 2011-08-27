import re
from aufmachen.websites import BaseResource
from aufmachen.soupselect import select
from aufmachen.BeautifulSoup import BeautifulSoup

class Song(BaseResource):
    
    def detail_url(self, id):
        artist = id[0]
        title =  id[1]
        return 'http://www.last.fm/music/%s/_/%s/+tags' % (artist.lower().replace(' ', '+'), title.lower().replace(' ', '+'))
        
    def parse_detail(self, id, html):
        song = {}
        song['artist'] = id[0]
        song['title'] =  id[1]
        
        #last.fm puts some strange tag in its code that caused an error when it was left in.
        endash = unichr(0x2013)      
        html = unicode(html.replace('<!%s[if IE]><![endif]%s>' % (endash, endash), ''))
        
        soup = BeautifulSoup(html)
        tags = [cloudItem.text for cloudItem in select(soup, '#tagcloud .cloudItem')]
        song['tags'] = tags
        return song
        
song = Song()