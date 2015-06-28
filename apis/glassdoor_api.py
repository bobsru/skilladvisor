__author__ = 'shafi'

import json,os
import urllib2
import requests

ip = '10.0.2.15'
p_id = '38134'
p_key = 'krhfhJLHAzG'

url = 'http://api.glassdoor.com/api/api.htm?v=1&format=json&\
t.p='+p_id+'&t.k='+p_key+'=employersq=pharmaceuticals&userip=10.0.2.15&useragent=Mozilla/%2F4.0'

url1='curl http://api.glassdoor.com/api/api.htm?v=1&format=json&t.p=38134&t.k=krhfhJLHAzG&action=employers&q=pharmaceuticals&userip=10.0.2.15'

payload = {
           'v' : '1',
           'format': 'json',
           't.p': '38134',
           't.k' : 'krhfhJLHAzG',
           'action' : 'employers',
           'q' : 'pharmaceuticals',
           'userip' : '10.0.2.15'
        }
r = requests.post("http://api.glassdoor.com/api/api.htm", data=json.dumps(payload), headers = {'Content-type': 'application/json', 'User-agent': 'Mozilla/4.0'})
print r.headers
print url1
cmd = 'sh /tmp/test.sh'
running = os.popen(cmd)
print running


import httplib2
h = httplib2.HTTPConnectionWithTimeout
resp, content = h.request(url1, "GET")
print content