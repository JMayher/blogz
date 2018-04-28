from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'
space = "    "

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry = db.Column(db.String(60))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, entry, body, owner):
        self.entry=entry
        self.body=body
        self.owner=owner
        

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'addpost', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        valid = True
        usererror = ""
        usernameerror = ""
        passworderror = ""
        verifyerror = ""
        fielderror = ""
        
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            usererror = "User already exists"
            valid = False
            
        if len(username) < 3:
            usernameerror = "Username does not contain enough characters"
            valid = False
            
        if len(password) < 3:
            passworderror = "Password does not contain enough characters"
            valid = False
            
        if password != verify:
            verifyerror = "Password and Verify Password do not match"
            valid = False
            
        if username.strip() == "" or password.strip() == "" or verify.strip() == "":
            flash('One or more fields are invalid')
            
            valid = False
        if valid == False:
            return render_template('signup.html', usererror = usererror, usernameerror = usernameerror, passworderror = passworderror, verifyerror = verifyerror, fielderror = fielderror)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        

    return render_template('signup.html')
        

@app.route('/logout')
def logout():
    del session['username']
    flash('Logged Out')
    return redirect('/blog')

@app.route('/')
def index():
    user = User.query.all()
    blog = Blog.query.all()
    return render_template('index.html', users=user, blogs=blog)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User pasword incorrect, or user does not exit', 'error')


    return render_template('login.html')



@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    error = "Please fill in the title"
    error1 = "Please fill in the body"
    
    return render_template("newpost.html", title="Build a Blog!")

@app.route('/blog', methods=['GET','POST'])

def addpost():

    error = "Please fill in the title"
    error1 = "Please fill in the body"
    blog = Blog.query.all()
    user = User.query.all()

    
    if request.method == 'GET':
        username1 = request.args.get('user')
      
        id = request.args.get('id')
        if request.args.get('id'):
            post = Blog.query.get(id)
            user1=post.owner_id
            user2=User.query.get(user1)
            return render_template("singleblog.html", blog=post, user=user2)
        elif request.args.get('user'):
            userblog = Blog.query.filter_by(owner_id = username1)
            user3 = User.query.get(username1)
            return render_template("userpage.html", userblog=userblog, user=user3)
        else:
            
            return render_template("blog.html", title="Build a Blog!", blogs=blog, users=user)
        

    if request.method == 'POST':
        
        blog_name = request.form['entry']
        entry_name = request.form['body']
        if blog_name.strip() == "" and entry_name.strip() == "":
            return render_template("newpost.html", error=error, error1=error1)
        elif blog_name.strip() == "":
            return render_template("newpost.html", error=error, entry_name=entry_name)
        elif entry_name.strip() == "":
            return render_template("newpost.html", error1=error1, blog_name=blog_name)
        else:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(entry=blog_name, body=entry_name, owner=owner)
            db.session.add(new_blog)
            db.session.commit()
            
            return redirect("/blog?id={0}".format(new_blog.id))

  

if __name__ == '__main__':
    app.run()