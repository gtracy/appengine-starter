from google.appengine.ext import db

   
class User(db.Model):
    user              = db.UserProperty()
    userID            = db.StringProperty()
    email             = db.StringProperty()
    preferredEmail    = db.StringProperty()
    nickname          = db.StringProperty()
    profilePhoto      = db.BlobProperty()
    status            = db.StringProperty()
    first             = db.StringProperty()
    last              = db.StringProperty()
    createDate        = db.DateTimeProperty(auto_now_add=True)
    karma             = db.IntegerProperty()
    fbProfile_url     = db.StringProperty()
    access_token      = db.StringProperty()

    
class SystemEvent(db.Model):
    eventType = db.IntegerProperty()
    user      = db.ReferenceProperty(User)
    dateAdded = db.DateTimeProperty(auto_now_add=True)
    metaOne   = db.StringProperty(multiline=True)
    metaTwo   = db.StringProperty(multiline=True)
    