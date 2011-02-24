import os
import urllib
from hashlib import md5

from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from gaesessions import get_current_session

# Let's create our own simple users model to store the user's data and password hash

class MyUser(db.Model):
	email			= db.EmailProperty()
	display_name	= db.StringProperty()
	password_hash	= db.StringProperty()
	# and any other application specific data:
	past_view_count = db.IntegerProperty(default=0)

# A few helpful functions to keep the usage simple

def redirect_with_msg(h, msg, dst='/'):
	get_current_session()['msg'] = msg
	h.redirect(dst)
	
def render_template(h, file, template_vals):
	path = os.path.join(os.path.dirname(__file__), 'templates', file)
	h.response.out.write(template.render(path, template_vals))

def login_required(handler_method, *args):
	def check_login(self, *args):
		session = get_current_session()
		if not session.has_key('me'):
			self.redirect('/login')
			return
		else:
			handler_method(self, *args)
	return check_login
	
# The handlers for web pages

class MainPage(webapp.RequestHandler):
	
	@login_required
	def get(self):

		d = dict()
		session = get_current_session()
		if session.has_key('msg'):
			d['msg'] = session['msg']
			del session['msg'] # only show the flash message once

		if session.has_key('me'):
			d['user'] = session['me'] # THIS IS THE SERIALIZED DATASTORE USER OBJECT, SESSION IS SECURE!

		if session.has_key('pvsli'):
			session['pvsli'] += 1
		else:
			session['pvsli'] = 0
		d['num_now'] = session['pvsli']
			
		render_template(self, "index.html", d)


class LoginPage(webapp.RequestHandler):
	"""This page displays the login dialog"""
	def get(self):
		d = {}
		session = get_current_session()
		if session.has_key('msg'):
			d['msg'] = session['msg']
			del session['msg'] # only show the flash message once
		render_template(self, 'login.html', d)
			
class PasswordCheck(webapp.RequestHandler):
	"""This page receive the POST with login+password (it should always be accessed with SSL: app.yaml secure)"""
	def post(self):
		email = self.request.get('email')
		pas = md5( self.request.get('pas') ).hexdigest()
		display_name='Web user'

		# Here should be a true test for validity of the email and password (via a query to the database)
		user = MyUser.get_by_key_name(email)
		
		if not user:
			# In this moment we are creating all non-existing users
			user = MyUser(key_name=email, email=email, display_name=display_name, password_hash=pas)
			user.put()
		
		if user.password_hash != pas:
			redirect_with_msg(self, 'Wrong password', '/login')
			return

		session = get_current_session()
		if session.is_active():
			session.terminate()

		session['me'] = user
		session['pvsli'] = 0 # pages viewed since logging in

		redirect_with_msg(self, 'success!')

class LogoutPage(webapp.RequestHandler):
	def get(self):
		session = get_current_session()
		if session.has_key('me'):
			# update the user's record with total views
			user = session['me']
			user.past_view_count += session['pvsli']
			user.put()
			session.terminate()
			redirect_with_msg(self, 'Logout complete: goodbye ' + user.display_name)
		else:
			redirect_with_msg(self, "How silly, you weren't logged in")

# The WSGI Application

application = webapp.WSGIApplication([('/', MainPage),
									  ('/login', LoginPage),
									  ('/logout', LogoutPage),
									  ('/password_check', PasswordCheck), # should be on SSL!!!
									 ])

def main(): run_wsgi_app(application)
if __name__ == '__main__': main()
