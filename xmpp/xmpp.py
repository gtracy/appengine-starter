import logging

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from google.appengine.api import xmpp

class XmppHandler(webapp.RequestHandler):
    
    def post(self):
      message = xmpp.Message(self.request.POST)
      body = message.body
      logging.info("XMPP request! Sent form %s with message %s" % (message.sender,body))

      requestArgs = body.split()
      message.reply("got it... ")

## end XmppHandler()

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', XmppHandler),
                                         ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

