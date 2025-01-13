import click
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Association table for task dependencies
task_dependencies = db.Table(
    'task_dependencies',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('dependency_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    tasks = db.relationship('Task', backref='project', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.String(50), default='To Do')
    due_date = db.Column(db.Date, default=lambda: (datetime.utcnow() + timedelta(days=2)).date())
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    dependencies = db.relationship(
        'Task',  # Self-referential relationship
        secondary='task_dependencies',  # Association table
        primaryjoin='Task.id == task_dependencies.c.task_id',
        secondaryjoin='Task.id == task_dependencies.c.dependency_id',
        backref='dependents'
    )

class TaskTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    tasks = db.relationship('TemplateTask', backref='template', lazy=True, cascade='all, delete-orphan')

class TemplateTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.String(50), default='To Do')
    due_date_offset = db.Column(db.Integer, default=0)  # Days offset from the project start date
    template_id = db.Column(db.Integer, db.ForeignKey('task_template.id'), nullable=False
    )

# CLI command to initialize the database
@app.cli.command("init-db")
def init_db():
    db.create_all()
    click.echo("Initialized the database.")

# Route to display all projects
@app.route("/")
def index():
    projects = Project.query.all()
    return render_template("index.html", projects=projects)

@app.route("/add_template", methods=["GET", "POST"])
def add_template():
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        task_titles = request.form.getlist('task_title[]')
        task_descriptions = request.form.getlist('task_description[]')
        task_due_date_offsets = request.form.getlist('task_due_date_offset[]')

        # Create the template
        new_template = TaskTemplate(name=name, description=description)
        db.session.add(new_template)
        db.session.commit()

        # Add tasks to the template
        for i in range(len(task_titles)):
            new_template_task = TemplateTask(
                title=task_titles[i],
                description=task_descriptions[i],
                due_date_offset=int(task_due_date_offsets[i]),
                template_id=new_template.id
            )
            db.session.add(new_template_task)

        db.session.commit()
        flash('Template created successfully!')
        return redirect(url_for('index'))

    return render_template("add_template.html")

@app.route("/apply_template/<int:project_id>", methods=["GET", "POST"])
def apply_template(project_id):
    project = Project.query.get_or_404(project_id)
    templates = TaskTemplate.query.all()

    if request.method == "POST":
        template_id = request.form['template_id']
        template = TaskTemplate.query.get_or_404(template_id)

        # Create tasks based on the template
        for template_task in template.tasks:
            due_date = (datetime.utcnow() + timedelta(days=template_task.due_date_offset)).date()
            new_task = Task(
                title=template_task.title,
                description=template_task.description,
                status=template_task.status,
                due_date=due_date,
                project_id=project_id
            )
            db.session.add(new_task)

        db.session.commit()
        flash('Template applied successfully!')
        return redirect(url_for('project_detail', project_id=project_id))

    return render_template("apply_template.html", project_id=project_id, templates=templates)

# Route to add a new project
@app.route("/add_project", methods=["GET", "POST"])
def add_project():
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        new_project = Project(name=name, description=description)
        db.session.add(new_project)
        db.session.commit()
        flash('Project added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template("add_project.html")

# Route to add a project with tasks
@app.route("/add_project_with_tasks", methods=["GET", "POST"])
def add_project_with_tasks():
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']

        new_project = Project(name=name, description=description)
        db.session.add(new_project)
        db.session.commit()

        task_titles = request.form.getlist('task_title[]')
        task_descriptions = request.form.getlist('task_description[]')
        task_statuses = request.form.getlist('task_status[]')
        task_due_dates = request.form.getlist('task_due_date[]')

        for i in range(len(task_titles)):
            due_date = None
            if task_due_dates[i]:
                try:
                    due_date = datetime.strptime(task_due_dates[i], '%Y-%m-%d').date()
                except ValueError:
                    flash(f'Invalid date format for task {i + 1}. Please use YYYY-MM-DD.', 'error')
                    continue

            new_task = Task(
                title=task_titles[i],
                description=task_descriptions[i],
                status=task_statuses[i],
                due_date=due_date,
                project_id=new_project.id
            )
            db.session.add(new_task)

        db.session.commit()
        flash('Project and tasks added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template("add_project_with_tasks.html")

# Route to add a task to a project
@app.route("/add_task/<int:project_id>", methods=["GET", "POST"])
def add_task(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project_id).all()

    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        due_date_str = request.form['due_date']
        dependencies = request.form.getlist('dependencies[]')

        # Convert due_date_str to a date object (or use default if empty)
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.')
                return redirect(url_for('add_task', project_id=project_id))
        else:
            # Use the default due date (2 days from now)
            due_date = (datetime.utcnow() + timedelta(days=2)).date()

        # Create the task
        new_task = Task(
            title=title,
            description=description,
            status=status,
            due_date=due_date,
            project_id=project_id
        )
        db.session.add(new_task)
        db.session.commit()

        # Add dependencies
        for dependency_id in dependencies:
            dependency = Task.query.get(dependency_id)
            if dependency:
                new_task.dependencies.append(dependency)

        db.session.commit()
        flash('Task added successfully!')
        return redirect(url_for('project_detail', project_id=project_id))

    return render_template("add_task.html", project_id=project_id, tasks=tasks)

# Route to display project details
@app.route("/project_detail/<int:project_id>")
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template("project_detail.html", project=project)

# Route to edit a task
@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get_or_404(task.project_id)
    tasks = Task.query.filter_by(project_id=project.id).all()

    if request.method == "POST":
        task.title = request.form['title']
        task.description = request.form['description']
        task.status = request.form['status']
        due_date_str = request.form['due_date']
        dependencies = request.form.getlist('dependencies[]')

        # Convert due_date_str to a date object (or None if empty)
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.')
                return redirect(url_for('edit_task', task_id=task_id))

        # Update dependencies
        task.dependencies = []
        for dependency_id in dependencies:
            dependency = Task.query.get(dependency_id)
            if dependency:
                task.dependencies.append(dependency)

        db.session.commit()
        flash('Task updated successfully!')
        return redirect(url_for('project_detail', project_id=task.project_id))

    return render_template("edit_task.html", task=task, tasks=tasks)

# Route to delete a task
@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id

    # Remove the task from the dependencies of other tasks
    for dependent_task in task.dependents:
        dependent_task.dependencies.remove(task)

    # Delete the task
    db.session.delete(task)
    db.session.commit()

    flash('Task deleted successfully!')
    return redirect(url_for('project_detail', project_id=project_id))

# Route to mark a task as complete
@app.route("/complete_task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get_or_404(task.project_id)

    # Check if all dependencies are completed
    for dependency in task.dependencies:
        if dependency.status != 'Done':
            flash(f'Cannot complete task "{task.title}" because dependency "{dependency.title}" is not done.')
            return redirect(url_for('project_detail', project_id=task.project_id))

    task.status = "Done"
    db.session.commit()
    flash('Task marked as done!')
    return redirect(url_for('project_detail', project_id=task.project_id))

# Route to edit a project
@app.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        project.name = request.form['name']
        project.description = request.form['description']
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template("edit_project.html", project=project)

# Route to delete a project
@app.route("/delete_project/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)