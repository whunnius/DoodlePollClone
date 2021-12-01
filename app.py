from logging import exception
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    published = db.Column(db.Boolean,default=False)
    timezone = db.Column(db.String(200), nullable=False)
    # start = db.Column(db.DateTime, default = None)
    # finish = db.Column(db.DateTime, default = None)
    # location = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return '<Task %r>' % self.id


#task_content is the entered in poll name by the admin i.e "wewe"
#tasks is a list of tasks




@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        task_timezone = request.form['timezone']
        if(task_content != "" and task_timezone!= ""):
            new_task = Todo(content=task_content,timezone=task_timezone)
            
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
    
        return render_template('index.html',tasks=tasks)


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