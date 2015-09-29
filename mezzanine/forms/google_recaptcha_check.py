import sys

if sys.version_info[0]==3:
    import http.client as h,urllib.parse as u
    def st(a):
        return str(a,'iso-8859-1')
else:
    import httplib as h,urllib as u
    def st(a):
        return str(a)

import json

def google_recaptcha_validation(request,page,rip,response,secret):
    params = u.urlencode({'secret': secret, 'response': response, 'remoteip': rip})
    headers = {"Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"}
    conn = h.HTTPSConnection("www.google.com")
    conn.request("POST", "/recaptcha/api/siteverify", params, headers)
    response = conn.getresponse()
    if response.status==200:
        data=response.read()
        return json.loads(st(data))['success']
    return False


