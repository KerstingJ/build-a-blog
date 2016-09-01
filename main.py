#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, jinja2, os, re
from google.appengine.ext import db
from cgi import escape

#Constants lol no caps
template_dir = os.path.join(os.path.dirname(__file__), "templates")
#that auto escape tho
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   autoescape=True)

def render_temp(template_name, **kargs):
	""" render jinja templates with less typing """
	template = jinja_env.get_template(template_name)
	return template.render(**kargs)

class Posts(db.Model):
	title = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class NewPost(webapp2.RequestHandler):
	'''new post handler'''
	def get(self):
		#handle title error
		t_error = self.request.get('t_error')
		c_error = self.request.get('c_error')
		content = self.request.get("content")
		title = self.request.get("title")
		title = escape(title)
		content = escape(content)
		
		self.response.write(render_temp('newpost.html', t_error=t_error,
										c_error=c_error, content=content,
										title=title))

class AddPost(webapp2.RequestHandler):
	def post(self):
		title = self.request.get('post_title')
		text = self.request.get('post_content')
		
		# this chunk does the error handling
		error = ""
		if not title:
			error += "t_error=Enter A Title"
		else:
			error += "title=" + title
		
		if not text:
			error += "&c_error=Enter Content for Your Post"
		else:
			if "t_error" in error:
				error += "&content=" + text
		
		if error != ("title="+title):
			self.redirect("/?" + error)
		
		if title and text:
			p = Posts(title=title, content=text)
			p.put()
			
			self.redirect("/blog")

class Blog(webapp2.RequestHandler):
	''' handler for /blog '''
	def get(self):
		posts = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC LIMIT 5")
		self.response.write(render_temp('blog.html', posts=posts, title="Blog"))

class ViewPostHandler(webapp2.RequestHandler):
	''' handler for /blog/id instances '''
	def get(self, post_id):
		post_id = post_id if post_id and int(post_id) else ""
		posts = [Posts.get_by_id(int(post_id))]
		self.response.write(render_temp('blog.html', posts=posts, title=posts[0].title))
		

app = webapp2.WSGIApplication([
	('/', Blog),
	('/add', AddPost),
	('/blog', Blog),
	('/newpost', NewPost),
	#weird why did i have to add the extra bit
	webapp2.Route('/blog/<post_id:\d+>', ViewPostHandler)
], debug=True)
