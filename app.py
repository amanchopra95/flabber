from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from user import User
from form import LoginForm, RegistrationForm, UpdatePassword, ArticleForm, SearchEngine
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message


import requests, datetime, re


###########USERS COLLECTION##########
MONGODB_URI = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
client = MongoClient(MONGODB_URI)
db = client.get_database("project_users")
users = db.users
posts = db.posts



app = Flask(__name__)
app.config['SECRET_KEY'] = "ThisisAsEcReT!"

login_manager = LoginManager()
login_manager.init_app(app)

#####MAIL CONFIG#########
mail = Mail(app)
app.config['DEBUG'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your@gmail.com'
app.config['MAIL_PASSWORD'] = 'yourpassword'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
#######HOME PAGE#########
@app.route('/')
def index():
	title = "Blog"
	return render_template("index.html", title=title)


############LOGIN FORM##########
@app.route('/login',methods=['GET','POST'])
def login():
	title = "Login"
	error = None
	form = LoginForm()
	if request.method == 'POST' and form.validate_on_submit():
		user = users.find_one({'username' : form.username.data})

		if user :
			if User.validate_login(user['password'], form.password.data):
				user_obj = User(user['username'])
				login_user(user_obj)

				session['logged_in'] = True
				session['username'] = form.username.data

				flash('You are logged in','success')			
				return redirect(url_for("dashboard"))
			else:
				error = "Wrong Username or Password."
		else :
			error = "Wrong Username or Password."
	return render_template("login.html", form=form, title=title, error=error)



##########SIGNUP FORM#########
@app.route('/signup', methods=['GET','POST'])
def signup():
	title = "Registration Form"
	error = None
	form = RegistrationForm()

	if request.method == 'POST' and form.validate_on_submit():

		if users.find_one({'username' : form.username.data}) is None:

			hashpw = generate_password_hash(form.password.data)
			users.insert({'username' : form.username.data, 'password' : hashpw,
			 'name' : form.name.data, 'email' : form.email.data})
			
			new_user = User(form.username.data)
			login_user(new_user)
			
			session['logged_in'] = True
			session['username'] = form.username.data

			flash('Registration Successfull','success')
			return redirect(url_for("dashboard"))
		
		else:
			error = "Username already exists."
	
	return render_template("signup.html", form=form, title=title, error=error)



#########DASHBOARD#########
@app.route('/dashboard')
@login_required
def dashboard():
	title = "Dashboard"
	articles = posts.find({'author' : current_user.username})

	if articles:
		return render_template("dashboard.html", title=title, articles=articles)

	return render_template("dashboard.html", title=title)




#########ADD ARTICLE#########
@app.route('/add_article', methods=['GET','POST'])
@login_required
def add_article():
	title = "Blog"
	form = ArticleForm()

	if request.method == 'POST' and form.validate_on_submit():
		user = users.find_one({'username' : current_user.username})

		articles =  {'title' : form.title.data, 
					'body' : form.body.data, 
					'timestamp' : datetime.datetime.now().strftime('%d-%m-%Y %H:%M'),
					'user_id' : user['_id'],
					'author' : user['username'],
					'comments' : {}}

		if user:
			posts.insert(articles)

		flash('Article Created', 'success')
		return redirect(url_for('dashboard'))

	return render_template("add_article.html", form=form, title=title)



########SHOW ALL ARTICLES#########
@app.route('/articles')
@login_required
def articles():
	title = "Articles"

	articles = posts.find()
	return render_template("articles.html", title=title, articles=articles)



#######SHOW FULL ARTICLE#######
@app.route('/articles/<string:title>/')
def full_article(title):
	Title=title.replace('%20','_')
	article = posts.find_one({'title':title})
	return render_template("full_article.html", article=article, title=Title)



##########SEARCH###########
@app.route('/search/')
def search():
	title = "Search Results"

	search = request.args.get('search', '')
	articles = posts.find_one({'title' : search})
	return render_template("search.html", title=title, articles=articles)
	



########EDIT ARTICLE#########
@app.route('/edit/<string:title>/', methods=['GET', 'POST'])
@login_required
def edit(title):
	Title = "Edit Article"
	form = ArticleForm()
	article = posts.find_one({'title' : title})
	form.title.data = article['title']
	form.body.data = article['body']

	if request.method == 'POST' and form.validate_on_submit():
		title = request.form['title']
		body = request.form['body']
		posts.update_one({'_id' : article['_id']},{"$set" : {'title' : title, 'body' : body,
							'timestamp' : datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}})

		flash('Article Edited.','success')
		return redirect(url_for("articles"))
		
	return render_template("edit.html", article=article, title=Title, form=form)




########DELETE ARTICLE########
@app.route('/delete/<string:title>',methods=['POST'])
@login_required
def delete(title):
	article = posts.find_one({'title' : title})
	posts.delete_one({'_id' : article['_id']})
	flash('Article Deleted Succesfully.', 'success')
	return redirect(url_for('dashboard'))

#########MAILING APP#########
app.route('/')
def send_mail():
	msg = Message('Hey!', sender="flabbermails@gmail.com", recipients=['amanchopra954@gmail.com'])
	msg.body = "Hello, "+session['username']+", welcome to Flabber. We are glad to have you."
	mail.send(msg)
	return "Sent"
	

########LOGOUT ROUTE########
@app.route('/logout')
@login_required
def logout():
	logout_user()
	session.clear()
	flash('Logged Out', 'success')
	return redirect(url_for("index"))



########USER LOADING#########
@login_manager.user_loader
def load_user(username):
	u = users.find_one({"username" : username})
	if not u:
		return None
	return User(u['username'])




if __name__ == "__main__":
	app.run(port=8000, debug=True, use_reloader=True)