from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, TextAreaField
from wtforms.validators import InputRequired

class LoginForm(FlaskForm):
	username = StringField('username',validators=[InputRequired()])
	password = PasswordField('password', validators=[InputRequired()])

class RegistrationForm(FlaskForm):
	name = StringField('Name', [validators.DataRequired()])
	username = StringField('Username',[validators.DataRequired()])
	email = StringField('Email', [validators.DataRequired()])
	password = PasswordField('Password', [validators.DataRequired(), 
		validators.EqualTo('confirm', message='Password does not match' )])
	confirm = PasswordField('Confirm Password')

class UpdatePassword(FlaskForm):
	username = StringField('username', validators=[InputRequired()])
	old_password = StringField('password', validators=[InputRequired()])
	new_password = StringField('password', validators=[InputRequired()])

class ArticleForm(FlaskForm):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = TextAreaField('Body', [validators.Length(min=1)])

class SearchEngine(FlaskForm):
	search = StringField('search', [validators.Length(min=1, max=400)])
