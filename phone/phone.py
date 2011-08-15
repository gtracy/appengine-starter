import logging

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util

from phone import twilio

ACCOUNT_SID = "FIXME"
ACCOUNT_TOKEN = "FIXME"
API_VERSION = '2010-04-01'
CALLER_ID = 'FIXME'

def sendSMS(toPhone,text):
      account = twilio.Account(ACCOUNT_SID, ACCOUNT_TOKEN)
      sms = {
             'From' : CALLER_ID,
             'To' : toPhone,
             'Body' : text,
             }
      try:
          account.request('/%s/Accounts/%s/SMS/Messages' % (API_VERSION, ACCOUNT_SID),
                          'POST', sms)
      except Exception, e:
          logging.error("Twilio REST error: %s" % e)

## end sendSMS()

class InboundSMSHandler(webapp.RequestHandler):
    
    def post(self):
      message = xmpp.Message(self.request.POST)
      body = message.body
      logging.info("XMPP request! Sent form %s with message %s" % (message.sender,body))

      requestArgs = body.split()
      message.reply("got it... ")

## end InboundSMSHandler()


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/phone/sms', InboundSMSHandler),
                                         ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

