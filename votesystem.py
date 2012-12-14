import cgi
import cgitb
import random
cgitb.enable()

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

form = cgi.FieldStorage()
a=[]

class Category(db.Model):
    name = db.StringProperty(required=True)
    items = db.StringListProperty()

class Result(db.Model):
    name = db.StringProperty(required=True)
    resultlist = db.StringListProperty()

C1 = Category(name="Movies")
C1.items=["Ironman","Titanic","Avartar","LionKing"]
C1.put()

C2 = Category(name="Sports")
C2.items=["Tennis","Footbal","Basketball","Soccer"]
C2.put()


# Main page, there are three options for the user, create a new category, vote on the exist categories,
# or check the results.
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
                <div><input type="radio" name="choice" value="vote"> Vote a category</div><br />
                <div><input type="submit" value="Start!"></div>
              </form>
            </body>
            </html>""")
        else:
            self.redirect(users.create_login_url(self.request.uri))

# The page when the use choose the first option on the main page: create a new category.
class Createnewcateogry(webapp.RequestHandler):
        def post(self):
                form = cgi.FieldStorage()
                #self.response.headers['Content-Type'] = 'text/plain'
                self.response.out.write('<html><body>')
                #self.response.out.write("hi")
                cname=form.getvalue('cname')
                #print cname
                itemnames=form.getvalue('itemnames')
                self.response.out.write('Here is your new category: <b>%s</b>' % cname)
                self.response.out.write('<p> The items in this category are: <br />')
                list=[]
                itemlist=itemnames.split('\n')
                for item in itemlist:
                    self.response.out.write('%s<br />' % item)
                    list.append(item)
                #self.response.out.write('<p> %s' % list)

                # add new cateogry into database
                new=Category(name=cname)
                new.items=list
                new.put()



                self.response.out.write("<hr />")
                self.response.out.write("<li>Back to <a href='/'> Home Page</a></li></ul>")
                self.response.out.write('</body></html>')

class AA(webapp.RequestHandler):
        def post(self):
            category = form.getvalue("category")
            self.response.out.write("%s" % category)
            self.response.out.write("<p><b> Results for %s:</b></p>" %category)
            # get the item list from the Category Model
            query2 = Category.all()
            query2.filter('name =', category)
            citem1=[]
            for u in query2:
                #self.response.out.write("%s<br />" % x.items)
                citem1=u.items
            # get the result list from the Result Model
            query3 = Result.all()
            query3.filter('name =', category)
            citem2=[]
            for w in query3:
                #self.response.out.write("%s<br />" % x.items)
                citem2=w.resultlist
                
            # create the output table, four fields: item name, win, lose, wining persentage
            self.response.out.write("<table border='1'>")
            self.response.out.write("<tr><td>Item name</td><td>Wins</td><td>Losses</td><td>Percent wins</td></tr>")
            
            for v in citem1:
                 self.response.out.write("<tr>")
                 self.response.out.write("<td>%s</td>" % v)
                 winnum=0
                 losenum=0
                 for vitem in citem2:
                     #self.response.out.write("%s<br />" % vitem)
                     
                     winentry = vitem.split("/")[0]
                     if v == winentry:                         
                         winnum+=1
                     loseentry = vitem.split("/")[1]
                     self.response.out.write("%s,%s<br />" % (winentry,loseentry))
                #self.response.out.write("%s" % entry)
                     
                     if v == loseentry:
                         losenum+=1
                 self.response.out.write("<td>%s</td>" % winnum)
                 self.response.out.write("<td>%s</td>" % losenum)
                 self.response.out.write("<td>%s</td>" % (winnum*100/(winnum+losenum)))
                 
                 self.response.out.write("</tr>")
            self.response.out.write("</table><br />")
            self.response.out.write("<hr />")
            
# Form the selected category, random generate two items for user to vote.
# read the answer and write into result for later use.
class Votecategory(webapp.RequestHandler):
        def post(self):
                form = cgi.FieldStorage()
                #self.response.headers['Content-Type'] = 'text/plain'
                self.response.out.write('<html><body>')
                category = form.getvalue("category")
                if form.has_key("aftervote"):
                    
                    item =form["item"].value
                    # item in format win/lose
                    win = form.getvalue("item").split("/")[0]
                    lose = form.getvalue("item").split("/")[1]
                    self.response.out.write("<i>You voted for '%s' over '%s'.</i><br /><br />" %(win,lose))
                    a.append(item)
                    #self.response.out.write("%s" % a)
                    # save the result into model Result
                    new=Result(name=category)
                    new.resultlist=a
                    new.put()
                    self.response.out.write("<b>Current totals:</b>")
                    query1 = Result.all()
                    query1.filter('name =', category)
                    relist=[]
                    for y in query1:
                        relist=y.resultlist
                    #self.response.out.write("%s" % relist)
                    #dic= {}
                    win1=0
                    win2=0
                    for p in relist:
                        entry = p.split("/")[0]
                        #self.response.out.write("%s" % entry)
                        if entry == win:
                            win1+=1
                        elif entry == lose:
                            win2+=1
                        #dic[entry[0]] = entry[1]
                    #self.response.out.write("%s,%s" % (win1,win2))
                    self.response.out.write("<table border='1'><tr><td>"+win+"</td><td>"+str(win1)+"</td></tr>")
                    self.response.out.write("<tr><td>"+lose+"</td><td>"+str(win2)+"</td></tr></table>")
                    self.response.out.write("<hr />")
          
                category = form.getvalue("category")
                self.response.out.write("<b>Category: </b>%s<br/>" %category)
                # get the selected category.
                query = Category.all()
                query.filter('name =', category)
                citem=[]
                for x in query:
                    #self.response.out.write("%s<br />" % x.items)
                    citem=x.items
                #total=len(citem)
                slice = random.sample(citem, 2)
                #self.response.out.write("%s" % citem)
                item1=slice[0]
                item2=slice[1]

                # No matter which item win, it will always show as format win/lose.
                self.response.out.write("<form action='/vote' method='post' target='_self'>")
                self.response.out.write("<input type='radio' name='item' value='%s' />%s<br />" % (item1+"/"+item2,item1))
                self.response.out.write("<input type='radio' name='item' value='%s' />%s<br />" % (item2+"/"+item1,item2))
                self.response.out.write("<input type='hidden' name='category' value='%s'/><br />" %category)
                self.response.out.write("<input type='submit' name='aftervote' value='Vote!' />")
                self.response.out.write("<input type='submit' name='skip' value='Skip'/>")
                self.response.out.write("</form>")

                self.response.out.write("<hr />")
                #self.response.out.write("<ul><li>See <a href='?results=%s' >all results </a></li>" % category)
                #self.response.out.write("<li>Back to <a href='/sign'> Category</a></li>")
                #self.response.out.write("<li>Back to <a href='/'>Home page</a></li></ul>")
                
                self.response.out.write('<form action="/aa" method="post">')
                self.response.out.write("<input type='hidden' name='category' value='%s'/><br />" % category)
                self.response.out.write('<div><input type="submit" value="See all results"></div>')
                self.response.out.write("</form>")
                
                self.response.out.write('<form action="/sign" method="post">')
                self.response.out.write('<div><input type="submit" value="Back to Category"></div>')
                self.response.out.write("</form>")

                self.response.out.write('<form action="/" method="get">')
                self.response.out.write('<div><input type="submit" value="Back to Homepage"></div>')
                self.response.out.write("</form>")
                #self.response.out.write("<li>Back to <a href='/sign'> Category</a></li></ul>")
                self.response.out.write('</body></html>')


class Guestbook(webapp.RequestHandler):
    def post(self):
        #C1 = Category(name="Movies")
        #C1.items=["Ironman","Titanic","Avartar","LionKing"]
        #C1.put()
        #C1.delete()
        #address_k = db.Key.from_path(C1.name, C1.items)
        #db.delete(address_k)
        

        #C2 = Category(name="Sports")
        #C2.items=["Tennis","Footbal","Basketball","Soccer"]
        #C2.put()
        #C2.delete()

        
        categories = db.GqlQuery("SELECT * FROM Category")
        
        
        if self.request.get('choice')=="item":
            
            
            self.response.out.write('<html><body>')
            #self.response.out.write('%s' % Category.key())
            #print categories
            #print Movies.items
            #print Category.key()

            self.response.out.write(" <b>Following are the exist categories: </b><br />")
            for category in categories:
                    #self.response.out.write('%s' % category)
                    #category.delete()
                    #self.response.out.write("<form action='/start' method='post' target='_self'>")
                    #self.response.out.write("<input type=radio name=category value='%s'checked/>%s<br />" % (category.name,category.name))
                    
                    self.response.out.write('<p>%s :' % category.name)
                    self.response.out.write('%s<br />' % category.items)
            self.response.out.write("<hr />")
            self.response.out.write("If you want to create a new category, please enter the new category's info:<br/ >")
            #self.response.out.write("Click here to start vote: <input type='submit' name='aftervote' value='Start!'>")
            self.response.out.write("<form action='/make' method='post' target='_self'>")
            self.response.out.write("<p> New Category Name: <input type='text' name='cname'>")
            self.response.out.write("<p> Please imput the items in this category, one item each line:")
            self.response.out.write("<p> <textarea name='itemnames' rows='20' cols='20'>")
            self.response.out.write("</textarea><br />")
            self.response.out.write("<input type='submit' name='create' value='Submit'>")
            self.response.out.write('</body></html>')

        # List all the categoires and let user start                              
        else:
                self.response.out.write("Please choose the category you want to vote: <br />")
                for category in categories:
                    #category.delete()
                    self.response.out.write("<form action='/vote' method='post' target='_self'>")
                    self.response.out.write("<input type=radio name=category value='%s'checked/>%s<br />" % (category.name,category.name))
                    
                    #self.response.out.write('<b>%s</b> :' % category.name)
                    #self.response.out.write('<b>%s</b><br />' % category.items)
                self.response.out.write("Click here to start vote: <input type='submit' name='beforevote' value='Start!'>")
                self.response.out.write('</body></html>')

        self.response.out.write("<hr />")
        self.response.out.write("<li>Back to <a href='/'> Home Page</a></li></ul>")

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', Guestbook),
                                      ('/vote',Votecategory),
                                      ('/make',Createnewcateogry),
                                      ('/aa',AA)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
