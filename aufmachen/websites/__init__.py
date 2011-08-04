from aufmachen.crawler import get_url

class BaseResource(object):
    
    crawler = 'urllib'

    def list(self, **kwargs):
        html = self.get_list_html(**kwargs)
        return self.parse_list(html)
        
    def get(self, id):
        html = self.get_detail_html(id)
        return self.parse_detail(id, html)

    def get_list_html(self, **kwargs):
        return get_url(self.list_url(**kwargs), crawler=self.crawler)    
    
    def get_detail_html(self, id):
        return get_url(self.detail_url(id), crawler=self.crawler)    
    
        
