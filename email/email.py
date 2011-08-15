import logging

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from google.appengine.api import mail

from dataModel import *

EMAIL_SENDER_ADDRESS = 'fixme'

def send(subject,toEmail,body):
    # create an task to send email in background
    task = Task(url='/emailqueue', params={'subject':subject,
                                           'toEmail':toEmail,
                                           'body':body,
                                          })
    task.add('email')
## end send()

class EmailReceiver(webapp.RequestHandler):
    def post(self):
        logging.error("EmailReceiver needs to be implemented!")
        return
## end EmailReceiver

class EmailWorker(webapp.RequestHandler):
    def post(self):        
        try:
            logging.debug("email task running for %s", ownerEmail)
        
            # send email 
            message = mail.EmailMessage()
            message.sender =  EMAIL_SENDER_ADDRESS                
            message.subject = self.request.get('subject')
            message.to = self.request.get('toEmail')
            message.html = self.request.get('body')
            message.send()

        except apiproxy_errors.DeadlineExceededError:
            logging.info("DeadlineExceededError exception!?! Try to set status and return normally")
            self.response.clear()
            self.response.set_status(200)
            self.response.out.write("Task took to long for %s - BAIL!" % email)

## end EmailWorker

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/email/send', EmailWorker),
                                          ('/_ah/mail/.+', EmailReceiver),
                                         ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

