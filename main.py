from flask import Flask, render_template,request,session,redirect
# pip install flask-sqlalchemy
from flask_sqlalchemy import SQLAlchemy
# like this we can import flask alchemy feature for database connection
from datetime import datetime
# pip install flask-mail
# and import flask mail like below
from flask_mail import Mail
from werkzeug.utils import secure_filename
import json
import os
import math

os.chdir('C:\\Users\\ManishKumar\\Desktop\\Flask\\templates')

with open("config.json", 'r') as c:
    # json config passed to params
    params = json.load(c)["params"]
local_server = True
app = Flask(__name__ )
app.secret_key = 'super-secret-key'
# set app.secret_key for security reason

app.config['UPLOAD_FOLDER'] = params['upload_location']


# this part we need to do use smtp gmail setup and server of gmail username and password so it will send mail whenever user tried to contact you through contact
# page
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = 'True',
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-pass']
)




#this to apply mail setup which we have configured
mail = Mail(app)
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']


# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/codethebest'
# 'mysql:password//root:@localhost/codethebest' - syntax to add db
db = SQLAlchemy(app)
# to intialize db connection


# create table where we can add data to database
class Contacts(db.Model):
    """sno,name,phone_no,mesg,email,date"""
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_no = db.Column(db.String(20), nullable=False)
    mesg = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(20),nullable=False)
    date = db.Column(db.String(20), nullable=True)


class Posts(db.Model):
    """sno,name,phone_no,mesg,email,date"""
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(20), nullable=True)
    slug = db.Column(db.String(40), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20), nullable=True)
    img_file = db.Column(db.String(20), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]


    if (page ==1):
        prev = '#'
        next = "/?page=" + str(page+1)
    elif(page==last):
        prev = "/?page" + str(page-1)
        next = '#'
    else:
        prev = "/?page=" + str(page-1)
        next = "/?page" + str(page+1)


    return render_template('index.html',params=params,posts=posts,prev=prev,next=next)




# @app.route("/")
# def home():
#     # here we are passing template
#     posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
#     return render_template("index.html", params=params,posts=posts)

@app.route("/dashboard",methods=['GET','POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)


    if request.method == 'POST':
        username = request.form.get('uname')
        #it will take username entered on admin panel on post method
        userpass = request.form.get('pass')
        # it will take password entered on admin panel on post method
        if (username == params['admin_user'] and userpass == params['admin_password']):
            # here it will check whether admin user and password is correct or not from post method so user can login in
            #set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html',params=params,posts=posts)

    return render_template("login.html", params=params)


    #Pagination Logic
    # First page
    # prev button = #
    # next = page +1
    # #Middle
    # prev = prev -1
    # next = page +1
    # #Last
    # prev = page -1
    # next = #




@app.route("/post/<string:post_slug>", methods=['GET'])
# to apply slug on end point
def post_route(post_slug):
# we need to pass post slug which is variable as slug need to be passed in function definition to use it
    post = Posts.query.filter_by(slug=post_slug).first()
# here through above query we fetch post_slug content to post varaiable from database that we have created and choose first slug if you slug have multiple same name
# but keep in mind make slug should be unique
    return render_template("post.html", params=params,post = post)

@app.route("/about")
def about():
    return render_template("about.html", params=params)


@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    # if user logged in already
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno == '0':
                post = Posts(title=box_title, slug=slug, content=content, tagline=tline, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.tagline = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post)

@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')



@app.route("/logout")
def logout():
    session.pop('user')
    # here user session will be killed
    return redirect('/dashboard')


@app.route("/uploader",methods = ['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "Uploaded successfully"





@app.route("/contact",methods = ['GET', 'POST'])
# here as we need to add data we gonna use post method and get is by default method defined
def contact():
    # here it applying post method on data
    if (request.method == 'POST'):
        """adding entry to the database"""
        # to retrieve data from user
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        """sno,name,phone_no,mesg,email,date"""
        entry = Contacts(name= name,phone_no = phone,mesg = message,date = datetime.now(),email = email)
        # pass data to columns of class Contacts

        db.session.add(entry)
        # add data to db
        db.session.commit()
        # commit the data being added or changed
        # mail sending way
        mail.send_message('New message from   ' + name #here this is username which trying to contact you as you defined in class
                          ,sender = email, # user mail
                          recipients = [params['gmail-user']], #your mail
                          body = message + "\n" + phone + email

                          )


# render  contact.html and above data to contact through this template also we need to apply action method on contact end point and method which going to apply on it
#    see contact.html to check
    return render_template("contact.html", params=params)




app.run(debug=True)