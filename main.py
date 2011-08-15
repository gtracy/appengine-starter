#!/usr/bin/env python

import os
import logging

from django.utils import simplejson

from google.appengine.api import users
from google.appengine.api import images
from google.appengine.api.taskqueue import Task
from google.appengine.ext import db
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from dataModel import *

from users import user, facebook
from events import event

class MainHandler(user.BaseHandler):
    def get(self):
      user = self.current_user
      if user:
          if user.fbProfile_url:
              greeting = ('<span class="user-name">%s<br/><a href="javascript:void()" onclick="fbLogout()">sign out</a></span><img src=http://graph.facebook.com/%s/picture>' % (user.nickname,user.userID))
          else:
              greeting = ('%s (<a href="%s">sign out</a>)' % (user.nickname, users.create_logout_url("/")))
      else:
          greeting = '' #("<a href=\"%s\">Sign in with Google</a>" %
                        #'/_ah/login_required')#users.create_login_url("/"))
          # generate the html
          template_values = {'greeting':greeting,}
          path = os.path.join(os.path.dirname(__file__), 'templates/splash.html')
          self.response.out.write(template.render(path, template_values))
          
          #self.redirect("/splash.html")
          return
      
    
      # add the counter to the template values
      template_values = {'greeting':greeting,
                        }
      
      # generate the html
      path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
      self.response.out.write(template.render(path, template_values))

## end MainHandler


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/', MainHandler),
                                         ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
