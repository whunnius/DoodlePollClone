from logging import exception
import re
import datetime
import calendar
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time, timedelta, date
from flask_login import UserMixin, login_manager, login_user, LoginManager, login_required, logout_user, current_user
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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(userID):
    return User.query.get(int(userID))

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
    eventTitle = db.Column(db.String(200), default="")
    eventDate = db.Column(db.String(200), default="")
    
    def __repr__(self):
        return '<Task %r>' % self.id

class User(db.Model, UserMixin):
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    def get_id(self):
        return (self.userID)
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

class VoterForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=4,max=20)], render_kw={"placeholder": "Name"})
    email = StringField(validators=[InputRequired(), Length(min=4,max=40)], render_kw={"placeholder": "Email"})
    notes = StringField(validators=[InputRequired(), Length(min=4,max=10000)], render_kw={"placeholder": "Notes"})

def findDay(date):
    born = datetime.strptime(date, '%Y %m %d').weekday()
    return (calendar.day_name[born])

def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta

@app.route('/', methods = ['GET'])
def home():
    return render_template('home.html')
'''
def voter():
    voter = Todo.query.filter_by(id=1).first() #TODO change filter needs to be by admin
    #TODO get time interval from db
    timeInterval = 30

    monthDict={1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    startDetails = "2021-12-02 09:30" #TODO get from db
    endDetails = "2021-12-02 11:30" #TODO get from db
    year = int(startDetails[:4])
    month = int(startDetails[5:7])
    day = int(startDetails[8:10])
    startTimeHour = int(startDetails[11:13])
    startTimeMin = int(startDetails[14:])
    endTimeHour = int(endDetails[11:13])
    endTimeMin = int(endDetails[14:])

    dts = [dt.strftime('%Y-%m-%d %H:%M ') for dt in 
       datetime_range(datetime(year, month, day, startTimeHour,startTimeMin), datetime(year, month, day, endTimeHour,endTimeMin), 
       timedelta(minutes=timeInterval))]

    timesArr = []
    for x in dts:
        timesArr.append(x[11:16])
    timesArr.append(endDetails[11:])     #adds the last time slot ex./ 10:30-11 if 11 is end time
    numOfButtons = len(timesArr) - 1

    stringTimes = []
    for x in range(len(timesArr)-1):
        timeSlot = timesArr[x] + '-' + timesArr[x+1]
        stringTimes.append(timeSlot)

    #TODO in html page loop through and print out a button for each
    return render_template('voter.html', form=VoterForm(), pollTitle="Zoom Meeting", location=voter.location, timezone=voter.timezone, year=year,
        month=monthDict[month], day=day, numOfButtons=numOfButtons, dayType = findDay(startDetails[:10].replace('-',' ')), timeList=timesArr, timeSlot=stringTimes) #get location, timezone, deadline from db
'''

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                if form.username.data == "whunnius":
                    return redirect(url_for('admin'))
                else:
                    #Temporary
                    return redirect(url_for('admin'))

    return render_template('login.html', form=form)

@app.route('/register',methods = ['GET', 'POST'])
def register():
    form = RegistorForm()


    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username = form.username.data,email = form.email.data, password =hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return 'There was an issue adding user'
    return render_template('register.html', form=form)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    print("im here")
    if request.method == 'POST':
        task_eventTitle = request.form['eventTitle']
        task_eventDate = request.form['eventDate']
        task_content = request.form['content']
        task_timezone = request.form['timezone']
        task_location = request.form['location']
        task_description = request.form['description']
        print(task_content)
        print(task_timezone)
        print(task_eventDate)
        if(task_content != "" and task_timezone!= "" ):
            new_task = Todo(content=task_content,timezone=task_timezone,location=task_location,description=task_description,eventTitle=task_eventTitle)
            print("hi")
            try:
                print("hi")
                db.session.add(new_task)
                db.session.commit()
                print("hi") 
                return redirect('/admin')
            except:
                return 'There was an issue adding your Poll'
        else:
            
            return redirect('/admin')
            #enter invalid title
    else:
        print("here now")
        tasks = Todo.query.order_by(Todo.date_created).all()
        print(tasks)
        return render_template('admin.html',tasks=tasks, events=events)

@app.route('/my-link/')
def my_link():
  request.form.

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/admin')
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
            return redirect('/admin')
        except:
            return 'Issue updating Schedule'
    else:
        return render_template('update.html',task=task)

@app.route('/publish/<int:id>', methods=['GET', 'POST'])
def publish(id):
    task = Todo.query.get_or_404(id)
    if(task.published==False):
        task.published =True
    else:
        task.published =False
    try:
        db.session.commit()
        return redirect('/admin')
    except:
        return 'Issue publishing poll'



if __name__ == "__main__":
    db.create_all()

    app.run(debug=True)