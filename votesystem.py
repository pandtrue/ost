import cgi
import cgitb
cgitb.enable()

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

form = cgi.FieldStorage()       

class Category(db.Model):
    name = db.StringProperty(required=True)
    items = db.StringListProperty()

#Movies = Category(name="Movies",
                  #items=["Ironman","Titanic","Avartar","LionKing"])
#Movies.put()
#db.put(Movies)
        
class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            #self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write('<html><body>')
            self.response.out.write('Hello, ' + user.nickname())
            self.response.out.write("""
              <center><H1>Welcome to the voting system</H1></center>
              <form action="/sign" method="post">
                <div><input type="radio" name="choice" value="item"> Create a category</div>
                <div><input type="radio" name="choice" value="vote"> Vote a category</div>
                <div><input type="radio" name="choice" value="result"> Check result</div><br />
                <div><input type="submit" value="Start!"></div>
              </form>
            </body>
            </html>""")
        else:
            self.redirect(users.create_login_url(self.request.uri))

class Createnewcateogry(webapp.RequestHandler):
        def post(self):
                self.response.out.write("hi")

                
class Start(webapp.RequestHandler):
        def post(self):
                self.response.headers['Content-Type'] = 'text/plain'
                category = form.getvalue("category")
                print category
                #if form.has_key("aftervote"):
                #        item =form["item"].value
                #        print item
                #def post(self):
                #        category = form.getvalue("category")
                #        print category
    
        


class Guestbook(webapp.RequestHandler):
    def post(self):
        C1 = Category(name="Movies")
        C1.items=["Ironman","Titanic","Avartar","LionKing"]
        C1.put()
        #C1.delete()
        #address_k = db.Key.from_path(C1.name, C1.items)
        #db.delete(address_k)
        

        C2 = Category(name="Sports")
        C2.items=["Tennis","Footbal","Basketball","Soccer"]
        C2.put()
        #C2.delete()

        
        categories = db.GqlQuery("SELECT * FROM Category")
        
        
        if self.request.get('choice')=="item":
            
            
            self.response.out.write('<html><body>')
            #print categories
            #print Movies.items
            #print Category.key()

            self.response.out.write(" <b>Following are the exist categories: </b><br />")
            for category in categories:
                    category.delete()
                    #self.response.out.write("<form action='/start' method='post' target='_self'>")
                    #self.response.out.write("<input type=radio name=category value='%s'checked/>%s<br />" % (category.name,category.name))
                    
                    self.response.out.write('<p>%s :' % category.name)
                    self.response.out.write('%s<br />' % category.items)
            #self.response.out.write("Click here to start vote: <input type='submit' name='aftervote' value='Start!'>")
            self.response.out.write("<form action='/make' method='post' target='_self'>")
            self.response.out.write("<p> New Category Name: <input type='text' name='cname'>")
            self.response.out.write("<p> Please imput the items in this category, one item each line:")
            self.response.out.write("<p> <textarea name='itemnames' rows='20' cols='20'>")
            self.response.out.write("</textarea><br />")
            self.response.out.write("<input type='submit' name='create' value='Submit'>")
            self.response.out.write('</body></html>')

        # List all the categoires and let user start                              
        elif self.request.get('choice')=="vote":
                for category in categories:
                    category.delete()
                    self.response.out.write("<form action='/start' method='post' target='_self'>")
                    self.response.out.write("<input type=radio name=category value='%s'checked/>%s<br />" % (category.name,category.name))
                    
                    #self.response.out.write('<b>%s</b> :' % category.name)
                    #self.response.out.write('<b>%s</b><br />' % category.items)
                self.response.out.write("Click here to start vote: <input type='submit' name='aftervote' value='Start!'>")
                self.response.out.write('</body></html>')
                print "b"
        elif self.request.get('choice')=="result":
                print "c"
        else:
            self.response.out.write('<html><body>You choose:<pre>')
            self.response.out.write(cgi.escape(self.request.get('choice')))
            self.response.out.write('</pre></body></html>')
            #print "hi"

        self.response.out.write("<hr />")
        self.response.out.write("<li>Back to <a href='/'> Home Page</a></li></ul>")

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', Guestbook),
                                      ('/start',Start),
                                      ('/make',Createnewcateogry)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
