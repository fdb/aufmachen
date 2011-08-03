import calendar
import os
import subprocess
import time
import hashlib
import datetime
from random import uniform
from urllib import urlopen

MODULE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PHANTOM_SCRIPT = os.path.join(MODULE_DIRECTORY, 'retrieve.js')
CACHE_DIRECTORY = os.path.join(MODULE_DIRECTORY, '../tmp/cache')

def utc_now():
    return calendar.timegm(datetime.datetime.utcnow().timetuple())

_last_network_access = 0

TIME_LIMIT = 2
TIME_SPREAD = 2.0

def range_limit():
    global _last_network_access
    now = utc_now()
    if now - _last_network_access < TIME_LIMIT:
        secs = uniform(TIME_LIMIT-TIME_SPREAD, TIME_LIMIT+TIME_SPREAD)
        print "Sleeping for %.1f seconds..." % secs
        time.sleep(secs)
        _last_network_access = now
        
def phantomjs_retrieve(url):
    range_limit()
    print "Retrieving", url
    process = subprocess.Popen(['phantomjs', PHANTOM_SCRIPT, url], stdout=subprocess.PIPE)
    out = process.communicate()
    process.wait()
    return out[0]
    
def urllib_retrieve(url):
    range_limit()
    print "Retrieving", url
    return urlopen(url).read().decode('utf-8', 'ignore')

def cache_path_for_url(url):
    """Return the path where the URL might be cached."""
    m = hashlib.md5()
    m.update(url)
    digest = m.hexdigest()
    return os.path.join(CACHE_DIRECTORY, '%s.html' % digest)
    
CRAWLERS = {
   'urllib': urllib_retrieve,
   'phantomjs': phantomjs_retrieve
}

def _ensure_directory(dirname):
    try:
        os.makedirs(dirname)
    except OSError: # File exists
        pass

def get_url(url, cached=True, crawler='urllib'):
    """Retrieves the HTML code for a given URL.
     If a cached version is not available, uses phantom_retrieve to fetch the page.
    cached - If True, retrieves the URL from the cache if it is available. If False, will still store the page in cache.
    Returns the HTML code of the page.
    """
    cache_path = cache_path_for_url(url)
    if cached and os.path.exists(cache_path):
        with open(cache_path) as f:
            html = f.read().decode('utf-8')
    else:
        crawler_fn = CRAWLERS[crawler]
        html = crawler_fn(url)
        _ensure_directory(CACHE_DIRECTORY)
        with open(cache_path, 'w') as f:
            f.write(html.encode('utf-8'))
    return html
    
if __name__=='__main__':
    print get_url('http://nodebox.net')