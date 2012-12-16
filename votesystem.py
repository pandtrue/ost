import cgi
import cgitb
import random
import os
import xml.dom.minidom
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

cgitb.enable()
form = cgi.FieldStorage()
a=[] # list use for store result.

# The model use for the different categories, contain name and items save in the category
class Category(db.Model):
    name = db.StringProperty(required=True)
    items = db.StringListProperty()
    
# The model use for save the vote result for each category, contain name of the cateogry
# and the list of result in format "winitem/loseitem"
class Result(db.Model):
    name = db.StringProperty(required=True)
    resultlist = db.StringListProperty()

class Belong(db.Model):
    user = db.StringProperty(required=True)
    categorylist = db.StringListProperty()

C1 = Category(name="Movies")
C1.items=["Ironman","Titanic","Avartar","LionKing"]
C1.put()

C2 = Category(name="Sports")
C2.items=["Tennis","Football","Basketball","Soccer"]
C2.put()


# Main page, there are two options for the user, first option is edit a category, which include:
# create new category; delete exist category; change name of a exist category;
# change name of a item in a category; import/export a category with XML.
# Second option is vote a category, user can choose to vote on different category,
# also, they can check the voting result on the category they vote on.
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
                <div><input type="radio" name="choice" value="item" checked/> Edit a category</div>
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

                # Check whether it is (part of)category name first
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

                # Check whether it is (part of) item name in any catgegory
                for u in query:
                    ilist=u.items
                    for w in ilist:
                        if word.lower() in w.lower():                           
                            self.response.out.write('%s is the name of a item(%s) in the category: %s<br />' % (word,w,u.name))
                            count+=1
                            
                # nothing found, reply item is not category or item in any category.
                if count==0:
                    self.response.out.write("Sorry, %s is not a category or a item in any cateogry...<br />" % word)

                self.response.out.write("<hr />")
                self.response.out.write("<li>Back to <a href='/'> Home Page</a></li></ul>")
                self.response.out.write('</body></html>')

# Create new category based on the infomation that user input, parse the content for items, each line one item.
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
                b=[]
                itemlist=itemnames.split('\n')
                for item in itemlist:
                    self.response.out.write('%s<br />' % item)
                    b.append(item)
                #self.response.out.write('<p> %s' % list)

                # add new cateogry into database
                new=Category(name=cname)
                new.items=b
                new.put()

                self.response.out.write("<hr />")
                self.response.out.write("<li>Back to <a href='/'> Home Page</a></li></ul>")
                self.response.out.write('</body></html>')

# This class contains several functions, inlcude: delete an exist category;
# export an exist category; change a category name; change a item name in a category;
# and delete a item in a category, more details addressed before each functions.
class Deletecategory(webapp.RequestHandler):
    def post(self):
                form = cgi.FieldStorage()
                self.response.out.write('<html><body>')
                category = form.getvalue("category")

                user = users.get_current_user()
                # Delete a category. also delete that category in the Result model.
                if form.has_key("deletecategory"):
                    blist=[]
                    queryu=Belong.all()
                    queryu.filter('user =', user)
                    for usr in queryu:
                        blist=queryu.categorylist
                        
                    query = Category.all()
                    query.filter('name =', category)
                    for x in query:
                        x.delete()
                        
                    query2 = Result.all()
                    query2.filter('name =', category)
                    for y in query2:
                        y.delete()
                           
                    self.response.out.write('Successfully delete the category!')
                    '''
                    if x in blist:
                        x.delete()
                        query2 = Result.all()
                        query2.filter('name =', category)
                        for y in query2:
                            y.delete()
                           
                        self.response.out.write('Successfully delete the category!')
                    else:
                        self.response.out.write('Sorry, this is not your category, you cannot delete it.')
                    '''
                    

                # Export a category, output the category in the xml format.
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


                # Change the name of a category.
                # First find out that category, get the items in it.
                # make the new category with new name and the same items, then delete old one.
                # For the result model, do the same way.
                elif form.has_key("changecategory"):
                    newname=form.getvalue("newname")
                    query = Category.all()
                    sameitem=[]
                    query.filter('name =', category)
                    for x in query:
                        sameitem=x.items
                        x.delete()
                    new=Category(name=newname)
                    new.items=sameitem
                    new.put()

                    query2 = Result.all()
                    sameresult=[]
                    query2.filter('name =', category)
                    for y in query2:
                        sameresult=y.resultlist
                        y.delete()
                    new=Result(name=newname)
                    new.resultlist=sameresult
                    new.put()
                    
                    self.response.out.write('Successfully change the category name!')

                # Delete an item in the category
                # get the item and find the category it in
                # delete that item in the item list and make new category with the new list and delete the old category
                # do the same thing in the result model, delete the row has item, create Result model with the new resultlist the delete the old one.
                elif form.has_key("deleteitem"):
                    item=form.getvalue("item")
                    query=Category.all()
                    itemlist=[]              
                    for x in query:
                        itemlist=x.items
                        if item in itemlist:
                            cname=x.name
                            
                            category=x
                            rightlist=itemlist
                            x.delete()
                            pos=rightlist.index(item)
                            rightlist.pop(pos)
                            new=Category(name=cname)
                            new.items=rightlist
                            new.put()

                    alist=[]
                    slist=[]
                    query2=Result.all()
                    for y in query2:
                        alist=y.resultlist                        
                        for u in xrange(len(alist)-1):
                            if item in alist[u]:
                                cname=y.name
                                pos=alist.index(alist[u])
                                alist.pop(pos)
                                y.delete()                   
                            new=Result(name=cname)
                            new.items=alist
                            new.put()
                    self.response.out.write("Successfully delete the item!")

                # Change the name of an exist item in a category
                # Find out the category that item in, get the item list, rename and make the new list
                # remake the category, and delete the old category
                # For Result model, do the same thing.                
                elif form.has_key("changeitem"):                    
                    newname=form.getvalue("newnameitem")
                    item=form.getvalue("item")
                    self.response.out.write("%s" % item)
                    self.response.out.write("%s" % newname)
                    query=Category.all()

                    itemlist=[]
                    for x in query:
                        itemlist=x.items
                        self.response.out.write("%s" % itemlist)
                        for u in xrange(len(itemlist)):
                            if item == itemlist[u]:
                                cname=x.name
                                self.response.out.write("%s" % itemlist[u])                         
                                pos=itemlist.index(itemlist[u])
                                self.response.out.write("%s" % pos)
                                itemlist.pop(pos)
                                itemlist.append(newname)
                                self.response.out.write("%s" % itemlist)
                                x.delete()
                                new=Category(name=cname)
                                new.items=itemlist
                                new.put()

                    alist=[]
                    query2=Result.all()
                    for y in query2:
                        alist=y.resultlist
                        for u in xrange(len(alist)-1):
                            if item in alist[u]:
                                bname=y.name                       
                                pos=alist.index(alist[u])
                                alist.pop(pos)                                                            
                                a=alist[u].split('/')
                                left=str(a[0])
                                right=str(a[1])
                                if item == left:
                                    b=(newname+'/'+right).decode('unicode-escape')
                                else:
                                    b=(left+'/'+newname).decode('unicode-escape')
                                alist.append(b)
                                self.response.out.write("%s" % alist)
                                y.delete()
                                new=Result(name=bname)
                                new.resultlist=alist
                                new.put()
                                self.response.out.write("%s" % new.resultlist)

                    query3 = Result.all()
                    citem2=[]
                    for w in query3:
                        citem2=w.resultlist
                        self.response.out.write("%s" %citem2)
                    self.response.out.write("Successfully change the name of item!")
                
                                            
                self.response.out.write("<hr />")
                self.response.out.write("<li>Back to <a href='/'> Home Page</a></li></ul>")
                self.response.out.write('</body></html>')

# create a category by import an xml page. First check whether the cateogry is already exist,
# if not, just add it in. If it already exist, replace the old one.
# For Result model, ex. item: A B C --> B C D. Check whether all the items in old category are in new one,
# if not, delete the comparison contains A from the result model. 
class Importxml(webapp.RequestHandler):
    def post(self):
                form = cgi.FieldStorage()
                self.response.out.write('<html><body>')
                address=form.getvalue("xml")
                PROJECT_DIR = os.path.dirname(address)
                dom = xml.dom.minidom.parse(address)
                root = dom.documentElement
                nameNode = root.getElementsByTagName("NAME")[0]
                catename = nameNode.childNodes[0].nodeValue
                items = root.getElementsByTagName("ITEM")

                itemlist=[]    
                for item in items:
                    nameNode2 = item.getElementsByTagName("NAME")[0]
                    itemlist.append(nameNode2.childNodes[0].nodeValue)
                blist=itemlist
                slist=[]
                query=Category.all()
                query.filter('name =', catename)               
                for x in query:
                    x.delete()
                
                new=Category(name=catename)
                new.items=itemlist
                new.put()
                rlist=[]
                query2=Result.all()
                query2.filter('name =', catename)
                
                for x in query:
                    slist=x.items
                    for z in query2:
                        rlist=z.resultlist
                        for y in slist:
                            if y not in blist:                                
                                for u in xrange(len(rlist)-1):                                 
                                    if y in rlist[u]:
                                        pos=rlist.index(rlist[u])
                                        rlist.pop(pos)
                            z.delete()                      
                    new=Result(name=catename)
                    new.resultlist=rlist
                    new.put()      
                    
                self.response.out.write("Successfully import a category with XML!")
                self.response.out.write("<hr />")
                self.response.out.write("<li>Back to <a href='/'> Home Page</a></li></ul>")
                self.response.out.write('</body></html>')
             
# Form the selected category, random generate two items for user to vote.
# read the answer and write into result for later use.
class Votecategory(webapp.RequestHandler):
        def post(self):
                form = cgi.FieldStorage()
                self.response.out.write('<html><body>')
                category = form.getvalue("category")
                if form.has_key("aftervote"):
                    item =form["item"].value
                    # item in format win/lose
                    win = form.getvalue("item").split("/")[0]
                    lose = form.getvalue("item").split("/")[1]
                    self.response.out.write("<i>You voted for '%s' over '%s'.</i><br /><br />" %(win,lose))
                    a.append(item)
                    self.response.out.write("%s" % a)
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
                    win1=0
                    win2=0
                    for p in relist:
                        entry = p.split("/")[0]
                        if entry == win:
                            win1+=1
                        elif entry == lose:
                            win2+=1

                    self.response.out.write("<table border='1'><tr><td>"+win+"</td><td>"+str(win1)+"</td></tr>")
                    self.response.out.write("<tr><td>"+lose+"</td><td>"+str(win2)+"</td></tr></table>")
                    self.response.out.write("<hr />")
                    
                # Check the result.
                # Create the table, first put in all the items in the selected category.
                # Then read the Result model of that category, parse the result and fill in the table.
                elif form.has_key("check"):
                    category = form.getvalue("category")
                    self.response.out.write("<p><b> Results for %s:</b></p>" %category)
                    query2 = Category.all()
                    query2.filter('name =', category)
                    citem1=[]
                    for u in query2:
                        citem1=u.items
                    # get the result list from the Result Model
                    query3 = Result.all()
                    query3.filter('name =', category)
                    citem2=[]
                    for w in query3:
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
                             winentry = vitem.split("/")[0]
                             if v == winentry:                         
                                 winnum+=1
                             loseentry = vitem.split("/")[1]
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
                    
                # This part shows on every page when the user vote on a category or check the result.
                # include two randomly generated items in that cateogry and buttons and options retuan to other pages.
                category = form.getvalue("category")
                self.response.out.write("<b>Category: </b>%s<br/>" %category)
                # get the selected category.
                query = Category.all()
                query.filter('name =', category)
                citem=[]
                for x in query:
                    citem=x.items
                slice = random.sample(citem, 2)
                item1=slice[0]
                item2=slice[1]

                # No matter which item win, it will always show as format win/lose.
                # This form include two radio item iputs, vote button and skip button, and check result button.
                self.response.out.write("<form action='/vote' method='post' target='_self'>")
                self.response.out.write("<input type='radio' name='item' value='%s' checked//>%s<br />" % (item1+"/"+item2,item1))
                self.response.out.write("<input type='radio' name='item' value='%s' />%s<br />" % (item2+"/"+item1,item2))
                self.response.out.write("<input type='hidden' name='category' value='%s'/><br />" %category)
                self.response.out.write("<input type='submit' name='aftervote' value='Vote!' />")
                self.response.out.write("<input type='submit' name='skip' value='Skip'/>")
                self.response.out.write("<hr />")
                self.response.out.write('<div><input type="submit" name="check" value="See all results"></div>')
                self.response.out.write("</form>")

                # This form contains back to category button.
                self.response.out.write('<form action="/sign" method="post">')
                self.response.out.write('<div><input type="submit" value="Back to Category"></div>')
                self.response.out.write("</form>")

                # This form contains back to homepage button.
                self.response.out.write('<form action="/" method="get">')
                self.response.out.write('<div><input type="submit" value="Back to Homepage"></div>')
                self.response.out.write("</form>")
                self.response.out.write('</body></html>')


# The page shows both when the user choose edit a category, includes four parts,
# Delete a Edit/Export a category; Create a new category; Import a category with XML;
# and the option back to homepage. Also the page when user choose vote on a category.
# Details before each part.
class Guestbook(webapp.RequestHandler):
    def post(self):
        categories = db.GqlQuery("SELECT * FROM Category")      
        if self.request.get('choice')=="item":           
            self.response.out.write('<html><body>')
            self.response.out.write(" <b>Edit a categorie/Export a category: </b><br />")
            # The part shows all the categories and items in each categories.
            # Also the button for export category; button for delete a category;
            # text area and button for change the name of a selected category to the new name user input.
            # text area and button for change the name of a selected item in that category to the new name user input.
            self.response.out.write("<form action='/delete' method='post' target='_self'>")
            for category in categories:

                    self.response.out.write("<input type=radio name=category value='%s'checked/>%s<br />" % (category.name,category.name))
                    citem=[]
                    citem=category.items
                    for item in citem:
                        self.response.out.write("&nbsp;&nbsp;&nbsp;&nbsp;<input type=radio name=item value='%s'checked/>%s" % (item,item))
                    self.response.out.write('<br /><br />')
                    #self.response.out.write('<b>%s</b> :' % category.name)
                    #self.response.out.write('<b>%s</b><br />' % category.items)

            self.response.out.write("<p>Click here to export category with XML: <input type='submit' name='export' value='Export'><br />")
            self.response.out.write("<p>Click here to delete a <b>cateogry</b>: <input type='submit' name='deletecategory' value='Deletes'><br />")
            self.response.out.write("<p>Change the name of this <b>cateogry</b> to: <input type='text' name='newname'>")
            self.response.out.write("<input type='submit' name='changecategory' value='Change'><br />")
            self.response.out.write("<p>Change the name of this <b>item</b> to: <input type='text' name='newnameitem'>")
            self.response.out.write("<input type='submit' name='changeitem' value='Change'><br />")
            self.response.out.write("<p>Click here to delete an <b>item</b>: <input type='submit' name='deleteitem' value='Deletes'><br />")
            self.response.out.write("</form>")
            self.response.out.write("<hr />")

            # The form use for add a new category. After user fill in the form and submit,
            # it will transfer to a new page and shows the information of that cateogry.
            self.response.out.write("<b>Create a new category:</b><br/ >")
            self.response.out.write("<form action='/make' method='post' target='_self'>")
            self.response.out.write("<p> New Category Name: <input type='text' name='cname'>")
            self.response.out.write("<p> Please imput the items in this category, one item each line:")
            self.response.out.write("<p> <textarea name='itemnames' rows='10' cols='20'>")
            self.response.out.write("</textarea><br />")
            self.response.out.write("<input type='submit' name='create' value='Submit'>")
            self.response.out.write("</form>")
            self.response.out.write('</body></html>')
            self.response.out.write("<hr />")

            # This form use for create new category with XML page user imported
            self.response.out.write("<b>Import a category with XML: </b><br/ >")
            self.response.out.write("<form action='/xml' method='post' target='_self'>")
            self.response.out.write("<p> Please enter the xml address: <input type='text' name='xml'>")
            self.response.out.write("<input type='submit' name='create' value='Import'>")
            self.response.out.write("</form>")
            
        # This page shows when user choose to vote on a category. List all the categoires and let user start                              
        else:
                self.response.out.write("Please choose the category you want to vote: <br />")
                for category in categories:
                    self.response.out.write("<form action='/vote' method='post' target='_self'>")
                    self.response.out.write("<input type=radio name=category value='%s'checked/>%s<br />" % (category.name,category.name))

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
