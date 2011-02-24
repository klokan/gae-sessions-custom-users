from gaesessions import SessionMiddleware

# suggestion: generate your own random key using os.urandom(64)
# WARNING: Make sure you run os.urandom(64) OFFLINE and copy/paste the output to
# this file.  If you use os.urandom() to *dynamically* generate your key at
# runtime then any existing sessions will become junk every time you start,
# deploy, or update your app!
import os
COOKIE_KEY = '\xd9\xd8fX\xe1;\x05\xbb\x9aa\x01\x82\x18\x85lL\t\xfeK\xb34\xe3H\xed\xe4[\xce\xce\r\xa8\x16\xeb\x0c\x1c\xc5\x9a\xa8\xcc\x10\xfd\xfe\xe2\xab\xc5j\xc93Oj\x9bt\x95\xaf\xbcB\xd1\xa0\x84\xee\r?P$c'
#'do not use this key'

def webapp_add_wsgi_middleware(app):
  from google.appengine.ext.appstats import recording
  app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
  app = recording.appstats_wsgi_middleware(app)
  return app
