#!/usr/bin/env python

import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.db import Key
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import memcache

from google.appengine.runtime import apiproxy_errors

from dataModel import *
from users import facebook
from events import event

class BaseHandler(webapp.RequestHandler):
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """
    @property
    def current_user(self):
        if users.get_current_user():
            user = users.get_current_user()
            localUser = db.GqlQuery("select * from User where userID = :1", user.user_id()).get()
            if not localUser:
                user = User(userID=user.user_id(),
                            nickname=user.nickname())
                user.put()
                self.redirect('/user/edit?userKey=%s' % user.key())
            else:
                user = localUser
            self._current_user = user
        elif not hasattr(self, "_current_user"):
            self._current_user = None
            cookie = facebook.get_user_from_cookie(self.request.cookies, 
                                                   facebook.FACEBOOK_APP_ID, 
                                                   facebook.FACEBOOK_APP_SECRET)
            if cookie:
                # Store a local instance of the user data so we don't need
                # a round-trip to Facebook on every request
                user = User.get_by_key_name(cookie["uid"])
                if not user:
                    graph = facebook.GraphAPI(cookie["access_token"])
                    try:
                        profile = graph.get_object("me")
                    except facebook.GraphAPIError:
                        self._current_user = None
                        return None
                    
                    user = User(key_name=str(profile["id"]),
                                userID=str(profile["id"]),
                                nickname=profile["name"],
                                fbProfile_url=profile["link"],
                                email=profile["email"],
                                access_token=cookie["access_token"])
                    logging.info("New User object created for %s (%s)" % (profile["name"],profile["id"]))
                    user.put()
                    
                    # log event
                    event.createEvent(event.EVENT_USER_ADD, user, None, profile["id"])

                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                self._current_user = user
        return self._current_user


class UserHandler(BaseHandler):
    
    def get(self):
      activeUser = self.current_user
      if activeUser:
          greeting = ("%s (<a href=\"%s\">sign out</a>)" %
                      (activeUser.nickname, users.create_logout_url("/")))
      else:
          self.redirect("/")
          return

      # identify the user profile being displayed
      userKey = self.request.get("user")
      if len(userKey) == 0:
          logging.debug("seeking profile page without a key...")
          userQuery = db.GqlQuery("SELECT __key__ FROM User WHERE userID = :1", activeUser.userID)
          userKey = userQuery.get()
          if userKey is None:
              logging.error("accessing a user not currently registered!?! how did this happen?")
              self.redirect('/')
              return
              
      logging.info("user key is %s" % userKey)
      user = db.get(userKey)
      if user is None:
          logging.info("Can't find this user!?! userKey sent from the client is %s" % userKey)
          # this should never be the case so bail back to the front page if it does
          self.redirect("/")
          return

      # get a list of skates this user has posted
      logging.info("query skates with user ID %s" % user.userID)
      skateQuery = db.GqlQuery("SELECT * FROM Skate WHERE owner = :1", user)
      # @fixme control the query limit better
      skates = skateQuery.fetch(20)
      status = ' '
      for s in skates:
          status = 'status goes here'

          logging.info("SKATE: %s" %b.title)
          results.append({'size':s.size,
                          'color':s.color,
                          'price':s.price,
                          'style':s.style,
                         })

      if user.userID == activeUser.userID:
          edit = '<div id="edit"><a href=/user/edit?user='+str(userKey)+'>edit</a></div>'
      else:
          edit = ' '

      # add the counter to the template values
      template_values = {'nickname':user.nickname,
                         'userEmail':user.email,
                         'userIDKey':str(user.key()),
                         'greeting':greeting,
                         'skates':results,
                         'edit':edit,
                        }
      
      # generate the html
      path = os.path.join(os.path.dirname(__file__), 'user.html')
      self.response.out.write(template.render(path, template_values))


##  end UserHandler
        
class UserEditHandler(BaseHandler):
    
    def get(self):
        user = self.current_user
        if user:
            logging.info("User: %s", user.nickname)
            if user.fbProfile_url:
                greeting = ('%s (<a href="javascript:void()" onclick="fbLogout()">sign out</a>)' % user.nickname)
            else:
                greeting = '<a href="%s">sign out</a>' % users.create_logout_url("/")
        
            nickname = first + ' ' + last if user.nickname is None else user.nickname
            email = user.email if user.preferredEmail is None else user.preferredEmail
        else:
            greeting = ''
            nickname = ''
            email = ''
            
        template_values = {'nickname':nickname,
                           'preferredEmail':email,
                           'greeting':greeting,
                           'userKey':self.request.get('userKey'),
                          }
        path = os.path.join(os.path.dirname(__file__), 'profile.html')
        self.response.out.write(template.render(path, template_values))
        
## end UserEditHandler

class ProfileAjaxUpdateHandler(webapp.RequestHandler):

    def post(self):
        activeUser = users.get_current_user()
        if activeUser is None:
            self.redirect("/")
            return

        first = self.request.get('first')
        last = self.request.get('last')
        nickname = self.request.get('nickname')
        email = self.request.get('email')
        userKey = self.request.get('userKey')
        
        user = db.get(userKey)
        if user is None:
            logging.error("Profile update attempt with no logged in user. This should never happen, %s" % userKey)
            return
        
        logging.info("Updating profile for %s with %s, %s, %s, %s" % (userKey,first,last,nickname,email))
        user.first = first
        user.last = last
        user.nickname = nickname
        user.email = email
        user.preferredEmail = email
        user.put()
        
        self.redirect('/')

## end ProfileAjaxUpdateHandler


def getUser(userID):
    
    user = memcache.get(userID)
    if user is None:
      userQuery = db.GqlQuery("SELECT * FROM User WHERE userID = :1", userID)
      users = userQuery.fetch(1)
      if len(users) == 0:
          logging.info("We can't find this user in the User table... userID: %s" % userID)
          return None
      else:
          memcache.set(userID, user)
          return users[0]
    else:
      return user
    
## end getUser()

def main():
  logging.getLogger().setLevel(logging.DEBUG)
  application = webapp.WSGIApplication([('/user', UserHandler),
                                        ('/user/edit', UserEditHandler),
                                        ('/user/update', ProfileAjaxUpdateHandler),
                                        ],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
