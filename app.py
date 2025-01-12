import click
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import logging 
from logging.handlers import RotatingFileHandler
from logging import Formatter
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    projects = db.relationship('Project', backref='user', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='project', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.String(50), default='To Do')
    due_date = db.Column(db.Date)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.cli.command("init-db")
def init_db():
    db.create_all()
    click.echo("Initialized the database.")

@app.route("/")
@login_required
def index():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", projects=projects)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template("register.html")

@app.route("/add_task/<int:project_id>", methods=["GET", "POST"])
@login_required
def add_task(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to add tasks to this project')
        return redirect(url_for('index'))
    
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        due_date_str = request.form['due_date']
        
        # Convert due_date_str to a date object (or None if empty)
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.')
                return redirect(url_for('add_task', project_id=project_id))
        
        new_task = Task(
            title=title,
            description=description,
            status=status,
            due_date=due_date,
            project_id=project_id
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template("add_task.html", project_id=project_id)

@app.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        new_project = Project(name=name, description=description, user_id=current_user.id)
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("add_project.html")

@app.route("/add_task/<int:project_id>", methods=["GET", "POST"])
@login_required
def add_task(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to add tasks to this project')
        return redirect(url_for('index'))
    if request.method == "POST":
        new_task = Task(
            title=request.form['title'],
            description=request.form['description'],
            status=request.form['status'],
            due_date=request.form['due_date'],
            project_id=project_id
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('project_detail', project_id=project_id))
    return render_template("add_task.html", project_id=project_id)

@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get_or_404(task.project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to edit this task')
        return redirect(url_for('index'))
    if request.method == "POST":
        task.title = request.form['title']
        task.description = request.form['description']
        task.status = request.form['status']
        task.due_date = request.form['due_date']
        db.session.commit()
        return redirect(url_for('project_detail', project_id=task.project_id))
    return render_template("edit_task.html", task=task)

@app.route("/delete_task/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get_or_404(task.project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to delete this task')
        return redirect(url_for('index'))
    project_id = task.project_id
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('project_detail', project_id=project_id))

@app.route("/complete_task/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get_or_404(task.project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to complete this task')
        return redirect(url_for('index'))
    task.status = "Done"
    db.session.commit()
    return redirect(url_for('project_detail', project_id=task.project_id))

@app.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to edit this project')
        return redirect(url_for('index'))
    if request.method == "POST":
        project.name = request.form['name']
        project.description = request.form['description']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("edit_project.html", project=project)

@app.route("/delete_project/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to delete this project')
        return redirect(url_for('index'))
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)