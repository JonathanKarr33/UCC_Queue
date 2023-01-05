from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
number_of_counselors = 4
individual_wait_time = 30


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def viewer():
    global number_of_counselors
    global individual_wait_time
    if request.method == 'POST':
        if 'ind_wait_time' in request.form and request.form['ind_wait_time'] != None:
            individual_wait_time = int(request.form['ind_wait_time'])
            request.form == None
            return redirect('/ucc_desk_portal')
        elif 'num_counselors' in request.form and request.form['num_counselors'] != None:
            number_of_counselors = int(request.form['num_counselors'])
            request.form == None
            return redirect('/ucc_desk_portal')
        elif 'content' in request.form:
            task_content = request.form['content']
            request.form == None
            new_task = Todo(content=task_content)
            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/ucc_desk_portal')
            except:
                return 'There was an issue adding your task'
    tasks = Todo.query.order_by(Todo.date_created).all()
    if (number_of_counselors > 0):
        wait_time = len(tasks) * individual_wait_time / number_of_counselors
    else:
        wait_time = -1
    return render_template('viewer.html', wait_time=wait_time, is_open = bool(number_of_counselors))

@app.route('/ucc_desk_portal', methods=['POST', 'GET'])
def index():
    #TODO: current submit for posts go to home page by defualt so I also have the function there temporarily and then redirect it back to this page. But it works
    global number_of_counselors
    global individual_wait_time
    if request.method == 'POST':
        if 'ind_wait_time' in request.form and request.form['ind_wait_time'] != None:
            print(request.form['ind_wait_time'])
            individual_wait_time = int(request.form['ind_wait_time'])
            tasks = Todo.query.order_by(Todo.date_created).all()
            return render_template('index.html', tasks=tasks, individual_wait_time=individual_wait_time, number_of_counselors=number_of_counselors)
        elif 'num_counselors' in request.form and request.form['num_counselors'] != None:
            number_of_counselors = int(request.form['num_councillors'])
            tasks = Todo.query.order_by(Todo.date_created).all()
            return render_template('index.html', tasks=tasks, individual_wait_time=individual_wait_time, number_of_counselors=number_of_counselors)
        elif 'content' in request.form:
            task_content = request.form['content']
            new_task = Todo(content=task_content)
            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/ucc_desk_portal')
            except:
                return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks, individual_wait_time=individual_wait_time, number_of_counselors=number_of_counselors)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/ucc_desk_portal')
    except:
        return 'There was a problem deleting that task'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/ucc_desk_portal')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)