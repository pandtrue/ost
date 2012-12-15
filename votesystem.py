import cgi
import cgitb
import random
import os
import xml.dom.minidom
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

cgitb.enable()

form = cgi.FieldStorage()
a=[]

# The model use for the different categories, contain name and items save in the category
class Category(db.Model):
    name = db.StringProperty(required=True)
    items = db.StringListProperty()
    
# The model use for save the vote result for each category, contain name of the cateogry
# and the list of result in format "winitem/loseitem"
class Result(db.Model):
    name = db.StringProperty(required=True)
    resultlist = db.StringListProperty()

C1 = Category(name="Movies")
C1.items=["Ironman","Titanic","Avartar","LionKing"]
C1.put()

C2 = Category(name="Sports")
C2.items=["Tennis","Football","Basketball","Soccer"]
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
                <div><input type="radio" name="choice" value="item"> Edit a category</div>
                <div><input type="radio" name="choice" value="vote"> Vote a category</div><br />
                <div><input type="submit" value="Start!"></div>
              </form>
              <hr >
              <form action='/find' method='post' target='_self'>
              <p> Want to find something? <br /><input type='text' name='finditem'>
              <input type='submit' name='create' value='Find!'>
              </form>
            </body>
            </html>""")
        else:
            self.redirect(users.create_login_url(self.request.uri))

# find the word that user input, and check is there any item in each category related to the word.
class Finditem(webapp.RequestHandler):
        def post(self):
                form = cgi.FieldStorage()               
                word=form.getvalue('finditem')
                self.response.out.write('<html><body>')
                #self.response.out.write('%s' % word)

                # Check category name first
                query = Category.all()
                namelist=[]
                ilist=[]
                count=0
                
                for u in query:
                    #self.response.out.write("%s<br />" % x.items)
                    namelist=u.name
                    #self.response.out.write('%s' % namelist)
                    if word.lower() in namelist.lower():
                        self.response.out.write('%s is the name of a category(%s)<br />' % (word,u.name))
                        count+=1
                    #else:
                        #self.response.out.write(" %s not found<br />" % word)
                    

                # Check whether in any catgegory
                for u in query:
                    ilist=u.items
                    for w in ilist:
                        if word.lower() in w.lower():                           
                            self.response.out.write('%s is the name of a itemCreate a new categos) in the category: %s<br />' % (word,w,u.name))
                            count+=1
                if count==0:
                    self.response.out.write("Sorry, %s is not a category or a item in any cateogry...<br />" % word)
                    #else:
                        #self.response.out.write(" %s not found" % word)

                self.response.out.write("<hr />")
                self.response.out.write("<li>Back to <a href='/'> Home Page</a></li></ul>")
                self.response.out.write('</body></html>')

# The page when the use choose the first option on the main page: create a new category.
class Createnewcategory(webapp.RequestHandler):
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

# Delete an exist category.
class Deletecategory(webapp.RequestHandler):
    def post(self):
                form = cgi.FieldStorage()
                self.response.out.write('<html><body>')
                category = form.getvalue("category")
                if form.has_key("delete"):
                    query = Category.all()
                    query.filter('name =', category)
                    for x in query:
                        x.delete()
                        
                    query2 = Result.all()
                    query2.filter('name =', category)
                    for y in query2:
                        y.delete()
                       
                    self.response.out.write('Category delete success!')

                # Export an category
                elif form.has_key("export"):
                    
                    
                    query = Category.all()
                    query.filter('name =', category)
                    relist=[]
                    for y in query:
                        relist=y.items

                    self.response.out.write(cgi.escape('<?xml version="1.0" encoding="UTF-8"?>'))
                    self.response.out.write('<br />')
                    self.response.out.write(cgi.escape("<CATEGORY>"))
                    self.response.out.write('<br />&nbsp;&nbsp;&nbsp;&nbsp;')
                    self.response.out.write(cgi.escape("<NAME>%s</NAME>\n" % category))
                    
                    for x in relist:
                        self.response.out.write('<br />&nbsp;&nbsp;&nbsp;&nbsp;')
                        self.response.out.write(cgi.escape("<ITEM>\n"))
                        self.response.out.write('<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
                        self.response.out.write(cgi.escape("<NAME>%s</NAME>\n" % x))
                        self.response.out.write('<br />&nbsp;&nbsp;&nbsp;&nbsp;')
                        self.response.out.write(cgi.escape("</ITEM>\n"))
                    self.response.out.write('<br />')
                    self.response.out.write(cgi.escape("</CATEGORY>\n"))

                    '''
                    with io.open('C:/Users/Tianyi/Desktop/ost/a.txt', 'w') as file:
                        file.write(u'Spam and eggs!')
                        file.close()
                    '''
                    
                    
                    '''
                    f.write(cgi.escape("<CATEGORY>\n"))
                    f.write(cgi.escape("<NAME>$s</NAME>\n" % category))
                    for x in relist:
                        f.write(cgi.escape("<ITEM>\n"))
                        f.write(cgi.escape("<NAME>%s</NAME>\n" % x))
                        f.write(cgi.escape("</ITEM>\n"))
                    f.write(cgi.escape("</CATEGORY>\n"))                   
                    f.close()
'''
                    
                self.response.out.write("<hr />")
                self.response.out.write("<li>Back to <a href='/'> Home Page</a></li></ul>")
                self.response.out.write('</body></html>')
                
# create a category by import an xml page.
class Importxml(webapp.RequestHandler):
    def post(self):
                form = cgi.FieldStorage()
                self.response.out.write('<html><body>')
                address=form.getvalue("xml")
                PROJECT_DIR = os.path.dirname('http://cs.nyu.edu/courses/fall12/CSCI-GA.3033-004/asgn/category.xml')
                #self.response.out.write("%s" % address)
                dom = xml.dom.minidom.parse('category.xml')
                root = dom.documentElement
                nameNode = root.getElementsByTagName("NAME")[0]
                catename = nameNode.childNodes[0].nodeValue
                self.response.out.write("%s" % catename)
                items = root.getElementsByTagName("ITEM")
                #n=root.getElementsByTagName("NAME")
                #self.response.out.write("%s" % n)
                #nameNode = item.getElementsByTagName("NAME")[0]
                #self.response.out.write("%s" % nameNode.childNodes[0].nodeValue)
                #for node in root.childNodes:
                itemlist=[]    
                for item in items:
                    #self.response.out.write("%s" % item.toxml())
                    nameNode2 = item.getElementsByTagName("NAME")[0]
                    #self.response.out.write("%s" % nameNode.nodeValue)
                    #nameNode = employee.getElementsByTagName("name")[0]
                    #self.response.out.write("%s" % nameNode.childNodes)
                    self.response.out.write("%s" % nameNode2.childNodes[0].nodeValue)
                    itemlist.append(nameNode2.childNodes[0].nodeValue)
                new=Category(name=catename)
                new.items=itemlist
                new.put()


                
                self.response.out.write("<hr />")
                self.response.out.write("<li>Back to <a href='/'> Home Page</a></li></ul>")
                self.response.out.write('</body></html>')
             
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

                elif form.has_key("check"):
                    category = form.getvalue("category")
                    #self.response.out.write("%s" % category)
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
                             #self.response.out.write("%s,%s<br />" % (winentry,loseentry))
                        #self.response.out.write("%s" % entry)
                             
                             if v == loseentry:
                                 losenum+=1
                         self.response.out.write("<td>%s</td>" % winnum)
                         self.response.out.write("<td>%s</td>" % losenum)
                         
                         if (winnum+losenum)==0:
                             winp=0
                         else:
                             winp=winnum*100/(winnum+losenum)
                         self.response.out.write("<td>%s</td>" % winp)
                         
                         self.response.out.write("</tr>")
                    self.response.out.write("</table><br />")
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
                self.response.out.write("<hr />")
                self.response.out.write('<div><input type="submit" name="check" value="See all results"></div>')
                self.response.out.write("</form>")

                #self.response.out.write("<hr />")
                #self.response.out.write("<ul><li>See <a href='?results' >all results </a></li>")
                #self.response.out.write("<li>Back to <a href='/sign'> Category</a></li>")
                #self.response.out.write("<li>Back to <a href='/'>Home page</a></li></ul>")
                
                #self.response.out.write('<form action="/aa" method="post">')
                #self.response.out.write("<input type='hidden' name='category' value='%s'/><br />" % category)
                #self.response.out.write('<div><input type="submit" name="check" value="See all results"></div>')
                #self.response.out.write("</form>")
                
                self.response.out.write('<form action="/sign" method="post">')
                self.response.out.write('<div><input type="submit" value="Back to Category"></div>')
                self.response.out.write("</form>")

                self.response.out.write('<form action="/" method="get">')
                self.response.out.write('<div><input type="submit" value="Back to Homepage"></div>')
                self.response.out.write("</form>")
                #self.response.out.write("<li>Back to <a href='/sign'> Category</a></li></ul>")
                self.response.out.write('</body></html>')


# the body of the program. if user choose edit a categoty, then he can create a new category
# or delete a exist category. If user choose to vote. the vote part start to work.
class Guestbook(webapp.RequestHandler):
    def post(self):
        
        categories = db.GqlQuery("SELECT * FROM Category")      
        if self.request.get('choice')=="item":
            
            self.response.out.write('<html><body>')
            self.response.out.write(" <b>Delete a categorie/Export a category: </b><br />")
            # The form for delete a exist category. If the category being deleted, it will shows on a new page.
            self.response.out.write("<form action='/delete' method='post' target='_self'>")
            for category in categories:
                    #self.response.out.write('%s' % category)
                    #category.delete()
                    #self.response.out.write("<form action='/start' method='post' target='_self'>")
                    #self.response.out.write("<input type=radio name=category value='%s'checked/>%s<br />" % (category.name,category.name))
                    
                    #self.response.out.write('<p>%s :' % category.name)
                    #self.response.out.write('%s<br />' % category.items)
                    #for category in categories:
                    #category.delete()
                    
                    self.response.out.write("<input type=radio name=category value='%s'checked/>%s<br />" % (category.name,category.name))
                    
                    #self.response.out.write('<b>%s</b> :' % category.name)
                    #self.response.out.write('<b>%s</b><br />' % category.items)
            self.response.out.write("<p>Click here to delete category: <input type='submit' name='delete' value='Deletes'><br />")
            self.response.out.write("<p>Click here to export category with XML: <input type='submit' name='export' value='Export'><br />")
            self.response.out.write("</form>")
            self.response.out.write("<hr />")


            self.response.out.write("<b>Create a new category:</b><br/ >")
            # The form for add a new category. After fill in the form and submit,
            # it will transfer to a new page and shows the information of that cateogry.
            self.response.out.write("<form action='/make' method='post' target='_self'>")
            self.response.out.write("<p> New Category Name: <input type='text' name='cname'>")
            self.response.out.write("<p> Please imput the items in this category, one item each line:")
            self.response.out.write("<p> <textarea name='itemnames' rows='10' cols='20'>")
            self.response.out.write("</textarea><br />")
            self.response.out.write("<input type='submit' name='create' value='Submit'>")
            self.response.out.write("</form>")
            self.response.out.write('</body></html>')
            self.response.out.write("<hr />")

            # create new category by import xml
            self.response.out.write("<b>Import a category with xml: </b><br/ >")
            self.response.out.write("<form action='/xml' method='post' target='_self'>")
            self.response.out.write("<p> Please enter the xml address: <input type='text' name='xml'>")
            self.response.out.write("<input type='submit' name='create' value='Import'>")
            self.response.out.write("</form>")
            

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

# The ternminal, use for transfer between different pages based on the action value.
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', Guestbook),
                                      ('/vote',Votecategory),
                                      ('/make',Createnewcategory),
                                      ('/delete',Deletecategory),
                                      ('/find',Finditem),
                                      ('/xml',Importxml)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
