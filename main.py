from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry = db.Column(db.String(60))
    body = db.Column(db.String(500))

    def __init__(self, entry, body):
        self.entry=entry
        self.body=body
        



@app.route('/newpost', methods=['GET', 'POST'])
def index():
    error = "Please fill in the title"
    error1 = "Please fill in the body"
    
    return render_template("newpost.html", title="Build a Blog!")

@app.route('/blog', methods=['GET','POST'])
def addpost():
    error = "Please fill in the title"
    error1 = "Please fill in the body"
    blog = Blog.query.all()

    if request.method == 'GET':
        
        id = request.args.get('id')
        if request.args.get('id'):
            post = Blog.query.get(id)
        
            return render_template("singleblog.html", blog=post)
        else:
            return render_template("blog.html", title="Build a Blog!", blogs=blog)
    

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
           
            new_blog = Blog(entry=blog_name, body=entry_name)
            db.session.add(new_blog)
            db.session.commit()
            
            return redirect("/blog?id={0}".format(new_blog.id))

  

if __name__ == '__main__':
    app.run()