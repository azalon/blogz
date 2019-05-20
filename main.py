from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body 
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password 
        

       

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title_error = ""
    body_error = ""

    


    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        
        if title == "":
            title_error += "Your post needs a title"
        if body == "":
            body_error += "Your post needs a body"
        if title_error or body_error:
            return render_template('new_post.html', title=title, body=body, title_error=title_error, body_error=body_error)
        
        owner = User.query.filter_by(username=session['user']).first()

        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        post_id = new_post.id
        return redirect('/blog?id=' + str(post_id))
            

      
        
        
    return render_template('new_post.html')



   


@app.route('/blog', methods=['GET'])
def get_posts():
    post_id= request.args.get('post_id')
    user = request.args.get('user')

    if post_id:
        blog = Blog.query.filter_by(id=int(post_id)).first()
        return render_template('single_post.html', blog=blog)
   
    elif user:
        owner = User.query.filter_by(username=user).first()
        all_posts = Blog.query.filter_by(owner=owner).all()
        return render_template('singleUser.html', owner=owner, all_posts=all_posts)

    else:
        all_posts = Blog.query.all()

    return render_template('blog.html', all_posts=all_posts, title="Blogz")


@app.route('/', methods=['GET'])
def index():
    users = User.query.all()

    return render_template('index.html', title="All Users", users=users)




@app.route('/signup', methods=['POST','GET'])
def signup():
    duplicate_error = ""
    username_error = ""
    password_error = ""
    verify_error = ""
    length_error = ""
    length_error_2 = ""
    password_error_2 = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_verify = request.form['password_verify']


        existing_user=User.query.filter_by(username=username).first()

   
        if password != password_verify:
            password_error_2 += "Your passwords do not match."  
        if existing_user:
            duplicate_error += "This username already exists"
        if username == "":
            username_error += "You need to enter a username"
        if password == "":
            password_error += "You need to enter a password"
        
        if password_verify == "":
            verify_error += "You need to re-enter password"
        if len(username) < 3:
            length_error += "Your username needs to be more than 3 characters"
        if len(password) < 3:
            length_error_2 += "Your password needs to be more than 3 characters"
        if username_error or verify_error or duplicate_error or length_error or length_error_2 or password_error or password_error_2:
            return render_template('signup.html', username=username, password=password, password_verify=password_verify, 
            username_error=username_error, password_error=password_error, verify_error=verify_error,
            length_error=length_error, length_error_2=length_error_2, password_error_2=password_error_2)
        else: 
            user = User(username, password)       
            db.session.add(user)
            db.session.commit()
            session['user'] = user.username
            return redirect('/newpost')
    else:
        return render_template('signup.html')
        
        
    @app.before_request
    def require_login():
        allowed_routes = ['login','blog','index','signup']
        if request.endpoint not in allowed_routes and 'user' not in session:
            redirect('/login')

   


    
    


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user'] = username
            flash("Logged in")
            return redirect('/newpost')
        if user and user.password != password:
            flash('User password incorrect')
            return redirect('/login')
        if not user:
            flash('Username does not exist')
            return redirect('/login')

    return render_template('login.html')

    #create account directs to /signup



@app.route('/logout')
def logout():
    del session['user']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()



    #line 61