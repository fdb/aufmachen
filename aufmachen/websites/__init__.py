from aufmachen.crawler import get_url

class BaseResource(object):
    
    crawler = 'urllib'

    def list(self, **kwargs):
        html = self.get_list_html(**kwargs)
        return self.parse_list(html)
        
    def get(self, id, cached=True):
        html = self.get_detail_html(id, cached)
        return self.parse_detail(id, html)

    def get_list_html(self, cached=True, **kwargs):
        return get_url(self.list_url(**kwargs), crawler=self.crawler, cached=cached)
    
    def get_detail_html(self, id, cached=True):
        return get_url(self.detail_url(id), crawler=self.crawler, cached=cached)
    
