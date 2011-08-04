import re
from time import strptime, strftime

from aufmachen.crawler import get_url, STATUS_OK
from aufmachen.scrapers import BaseScraper
from aufmachen.soupselect import select
from aufmachen.BeautifulSoup import BeautifulSoup

class SeriesScraper(BaseScraper):
    
    def detail_url(self, id):
        return 'http://epguides.com/%s/' % id
    
    def get(self, id):
        status, html = get_url(self.detail_url(id))
        if status != STATUS_OK:
            return None
        
        soup = BeautifulSoup(html)
        series = {}
        series['title'] = select(soup, 'h1 a')[0].text
        
        pre_text = unicode(select(soup, '#eplist pre')[0])
        seasons_html = pre_text.split('&bull;')[1:]
        seasons = []
        for season_html in seasons_html:
            season = {}
            season['number'] = int(re.search('Season (\d+)', season_html).groups(1)[0])
            episodes = []
            episodes_html = season_html.split('\n')[1:] # Ignore the "Season" line.
            for episode_html in episodes_html:
                m = re.match('^\s*(\d+)\s+(\d+)-(\d+)\s+(\w+)\s+(\d{2}\/\w{3}\/\d{2})\s+<a.*?>(.*?)<\/a>', episode_html)
                if m is None: continue
                data = m.groups(1)
                air_date = strptime(data[4], '%d/%b/%y')
                episode = {}
                episode['epid'] = int(data[0], 10)
                episode['season'] = int(data[1], 10)
                episode['number'] = int(data[2], 10)
                episode['production_number'] = data[3]
                episode['air_date'] = strftime('%Y-%m-%d', air_date)
                episode['title'] = data[5]
                episodes.append(episode)
            season['episodes'] = episodes
            seasons.append(season)
        series['seasons'] = seasons
        return series
        
series = SeriesScraper()