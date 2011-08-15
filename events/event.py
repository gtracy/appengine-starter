import logging

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util

from dataModel import SystemEvent


def createEvent(eventType, 
                metaOne='',
                metaTwo=''):

    # create an event to log the event
    task = Task(url='/event/new', params={'type':eventType,
                                           'metaOne':metaOne,
                                           'metaTwo':metaTwo
                                        })
    task.add('eventlog')
    
## end createEvent()    


class EventWorker(webapp.RequestHandler):
    def post(self):        
        logging.debug("EVENT: logging user event from %s, meta: %s" % (user.nickname,metaNoteOne))
        event = SystemEvent()
        event.eventType = self.get.request('type')
        event.metaOne = self.get.request('metaOne')
        event.metaTwo = self.get.request('metaTwo')
        event.put()

## end EventWorker

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/event/new', EventWorker),
                                         ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

