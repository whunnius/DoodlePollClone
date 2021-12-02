from logging import exception
import re
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin
from flask_wtf import FlaskForm
from flask_wtf.form import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'secretkey'




events = [{
    'todo' : 'Hi',
    'date' : '2021-11-23',
}]


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    published = db.Column(db.Boolean,default=False)
    timezone = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), default="")
    description = db.Column(db.String(1000), default="")
    
    def __repr__(self):
        return '<Task %r>' % self.id

class User(db.Model, UserMixin):
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    #password is set to 80 chars here because when registor form hashes the password we dont know how long the length of string will be. actual length is 20 chars

class RegistorForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4,max=20)], render_kw={"placeholder": "Username"})
    email = StringField(validators=[InputRequired(), Length(min=4,max=40)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4,max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        #existing_user_email = User.query.filter_by(email=email.data).first()

        if existing_user_username :
            raise ValidationError("Username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4,max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4,max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/register',methods = ['GET', 'POST'])
def register():
    form = RegistorForm()


    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username = form.username.data,email = form.email.data, password =hashed_password)
        print(form.username.data)
        print(form.email.data)
        print(hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            print("gigigig")
            return redirect(url_for('login'))
        except:
            return 'There was an issue adding user'
    return render_template('register.html', form=form)


@app.route('/', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        task_content = request.form['content']
        task_timezone = request.form['timezone']
        task_location = request.form['location']
        task_description = request.form['description']
        if(task_content != "" and task_timezone!= "" ):
            new_task = Todo(content=task_content,timezone=task_timezone,location=task_location,description=task_description)
            
            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except:
                return 'There was an issue adding your Poll'
        else:
            return redirect('/')
            #enter invalid title
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
    
        return render_template('admin.html',tasks=tasks, events=events)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting specific schedule'
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        print(task.content)
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Issue updating Schedule'
    else:
        return render_template('update.html',task=task)

@app.route('/publish/<int:id>')
def publish(id):
    task = Todo.query.get_or_404(id)
    if(task.published==False):
        task.published =True
    else:
        task.published =False
    try:
        db.session.commit()
        return redirect('/')
    except:
        return 'Issue publishing poll'



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)