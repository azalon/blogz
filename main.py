from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body 
       

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
        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()
        post_id = new_post.id
        return redirect('/blog?id=' + str(post_id))
            

      
        
        
    return render_template('new_post.html')



   


@app.route('/blog', methods=['GET'])
def get_posts():
    post_id= request.args.get('id')
    if post_id is not None:
        blog = Blog.query.get(post_id)
        return render_template('single_post.html', blog=blog)
    all_posts = Blog.query.all()
    
    return render_template('blog.html', all_posts=all_posts, title="Build A Blog", post_id=post_id)


@app.route('/', methods=['GET'])
def index():
    return redirect('/blog')



if __name__ == '__main__':
    app.run()