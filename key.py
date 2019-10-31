import base64
import hmac
import hashlib

f = open('lorem.txt', 'rb')
try:
    body = f.read()
finally:
    f.close()

digest = hmac.new(b'0123456789', body, hashlib.sha1).digest()
#print (base64.b64encode(digest))