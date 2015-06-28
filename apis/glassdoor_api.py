__author__ = 'srujanabobba'


gd_url = 'http://api.glassdoor.com/api/api.htm?v=1&format=json&t.p=38134&t.k=krhfhJLHAzG&&userip=10.0.2.15'
import urllib2
opener = urllib2.build_opener()
gd_full_url = gd_url + '&action=jobs-stats&returnStates=true&admLevelRequested=1&q=software%20engineer&returnJobTitles=true&returnEmployers=true'
req = urllib2.Request(gd_full_url, headers={ 'User-Agent': 'Mozilla/5.0' })
html = urllib2.urlopen(req).read()
print html
