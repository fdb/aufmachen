from aufmachen.crawler import get_url

class BaseResource(object):
    
    crawler = 'urllib'

    def get_detail_html(self, id):
        return get_url(self.detail_url(id), crawler=self.crawler)    
    
    def get(self, id):
        html = self.get_detail_html(id)
        return self.parse_detail(id, html)
    