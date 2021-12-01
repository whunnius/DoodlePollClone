from logging import exception
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
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


#task_content is the entered in poll name by the admin i.e "wewe"
#tasks is a list of tasks
# @app.route('/')
# def login():
#     return render_template('login.html')


# @app.route('/login',methods=["POST"])
# def loginAuth():
#     username = request.form['user_Id']
#     userPassword = request.form['password']
#     user = Todo.query.filter_by(user_Id=username, password=userPassword).first()

#     if user:
#         job_type = user.get_job()
#         if job_type == 'physician':
#             return redirect(url_for('physician', user_Id=user.user_Id))
#         else:
#             return job_type
#     else:
#         flash("Incorrect username or password", 'error')
#         return redirect(url_for('login'))




@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        task_timezone = request.form['timezone']
        task_location = request.form['location']
        task_description = request.form['description']
        if(task_content != "" and task_timezone!= "" ):
            new_task = Todo(content=task_content,timezone=task_timezone,location=task_location,description=task_description)
            
            try:
                print("here")
                db.session.add(new_task)
                print("here1")
                db.session.commit()
                print("here2")
                return redirect('/')
            except:
                return 'There was an issue adding your Poll'
        else:
            return redirect('/')
            #enter invalid title
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
    
        return render_template('index.html',tasks=tasks, events=events)


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