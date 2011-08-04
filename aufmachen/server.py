# Web server that serves JSON for resources.
#
# Get a single resource:
#
#     GET /:website/:resource/:id
#
# website - The website to fetch. This has to match the Python module name.
# resource - The resource available for this website.
# id - The id for this resource. This has to match how we parse IDs
#
# For example, for epguides.com:
#
#    GET http://127.0.0.1:8080/epguides/series/lost
#    >>> {
#          "title": "Lost", 
#          "seasons": [
#            {
#              "number": 1, 
#              "episodes": [
#                {
#                  "title": "Pilot (1)", 
#                  "season": 1, 
#                  "air_date": "2004-09-22", 
#                  "number": 1, 
#                  "production_number": "100", 
#                  "epid": 1
#                }, 
#                ...
#             ]
#            },
#            ...
#          ]
#        }

import json
import re

ONLY_LETTERS_RE = re.compile(r'[a-z]{3,100}')
ID_RE = re.compile(r'[A-Za-z0-9-]{1,100}')

def app(environ, start_response):
    paths = environ.get('PATH_INFO', '').split('/')
    
    if len(paths) < 3 or len(paths) > 4:
        start_response('404 Not Found', [('content-type', 'text/html')])
        return "Website / resource not found."

    website = ONLY_LETTERS_RE.match(paths[1]).group()
    resource = ONLY_LETTERS_RE.match(paths[2]).group()

    root_module = __import__('aufmachen.websites.%s' % website)
    website_module = getattr(root_module.websites, website)
    resource_parser = getattr(website_module, resource)

    if len(paths) == 3: # List view
        data = resource_parser.list()
    elif len(paths) == 4: # Detail view
        resource_id = ID_RE.match(paths[3]).group()
        data = resource_parser.get(resource_id)
        
    start_response('200 OK', [('content-type', 'text/html')])
    return json.dumps(data, indent=2)

if __name__=='__main__':
    # Make the root namespace available.
    import sys
    sys.path.append('..')
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8080')
