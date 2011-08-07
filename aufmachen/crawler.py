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
FAIL_IF_NOT_CACHED = False

class HttpNotFound(BaseException):
    pass

def utc_now():
    return calendar.timegm(datetime.datetime.utcnow().timetuple())

_last_network_access = 0

TIME_LIMIT = 10
TIME_SPREAD = 2.0

def range_limit():
    global _last_network_access
    now = utc_now()
    if (now - _last_network_access) < TIME_LIMIT:
        secs = uniform(TIME_LIMIT-TIME_SPREAD, TIME_LIMIT+TIME_SPREAD)
        print "Sleeping for %.1f seconds..." % secs
        time.sleep(secs)
    _last_network_access = utc_now()
        
def phantomjs_retrieve(url):
    """Retrieve the given URL using PhantomJS.
    PhantomJS will evaluate all scripts and return the HTML after body.onload.
    
    url - The page URL to retrieve
    
    Returns a status code (e.g. 200) and the HTML as a unicode string.
    """
    range_limit()
    print "pGET", url
    process = subprocess.Popen(['phantomjs', PHANTOM_SCRIPT, url], stdout=subprocess.PIPE)
    out = process.communicate()
    process.wait()
    response = out[0].decode('utf-8', 'ignore')
    status = response[:2]
    body = response[3:] # After the 'ok ' part.
    if status == 'ok':
        return 200, body
    else:
        return 404, body
    
def urllib_retrieve(url):
    """Retrieve the given URL using Python's built-in urllib.
    
    url - The page URL to retrieve
    
    Returns a status code (e.g. 200) and the HTML as a unicode string.
    """
    range_limit()
    print "uGET", url
    f = urlopen(url)
    html = f.read().decode('utf-8', 'ignore')
    return f.getcode(), html

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

    Returns the HTML as a unicode string.
    Raises a HttpNotFound exception if the page could not be found.
    """
    cache_path = cache_path_for_url(url)
    if cached and os.path.exists(cache_path):
        with open(cache_path) as f:
            html = f.read().decode('utf-8')
    else:
        if FAIL_IF_NOT_CACHED:
            raise BaseException("URL is not in cache and FAIL_IF_NOT_CACHED is True: %s" % url)
        crawler_fn = CRAWLERS[crawler]
        status, html = crawler_fn(url)
        if status != 200: 
            raise HttpNotFound(url)
        _ensure_directory(CACHE_DIRECTORY)
        with open(cache_path, 'w') as f:
            f.write(html.encode('utf-8'))
    return html
    
if __name__=='__main__':
    print get_url('http://nodebox.net/', crawler='phantomjs', cached=False)
