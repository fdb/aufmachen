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
        cloudItems = select(soup, '#tagcloud .cloudItem')
        tags = []
        for cloudItem in cloudItems:
            m = re.search('font-size: (\d+)px', cloudItem['style'])
            weigth = int(m.group(1)) if m is not None else -1
            tags.append((weigth, cloudItem.text))
        song['tags'] = tags
        return song

song = Song()