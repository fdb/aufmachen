Aufmachen
=========
Aufmachen comes knocking at the door of popular websites. Time to open up your data!

Aufmachen is a library for turning a website's HTML into nice, clean objects. 

Here's how to scrape epguides.com:

    from aufmachen.websites import epguides
    earl_series = epguides.series.get('mynameisearl')
    
    len(earl_series['seasons'])
    >>> 4

    earl_series['seasons'][0]['episodes'][0]
    >>> {'title': u'Pilot', 'season': 1, 'air_date': '2005-09-20', 'number': 1, 'production_number': u'1ALJ79', 'epid': 1}
        
We're building a repository of scrapers for popular websites. Come join us! 


Installing
----------
Aufmachen doesn't require any outside dependencies.

Optionally, Aufmachen can use phantomjs (http://www.phantomjs.org/) for web pages that load additional content using Ajax.


Authors
-------
Jan De Bleser <jandebleser@gmail.com>
Frederik De Bleser <frederik@burocrazy.com>

Aufmachen uses BeautifulSoup (http://www.crummy.com/software/BeautifulSoup/) by Leonard Richardson. Licensed under the Simplified BSD License.
Aufmachen uses soupselect.py (http://code.google.com/p/soupselect/) by Simon Willison. Licensed under the MIT License.