from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_smorest import Api, Blueprint, abort
from flask_restful import Resource
from datetime import datetime, timedelta
from marshmallow import Schema, fields, ValidationError

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['API_TITLE'] = 'Flask Task Manager API'
app.config['API_VERSION'] = 'v1'
app.config['OPENAPI_VERSION'] = '3.0.2'
app.config['OPENAPI_URL_PREFIX'] = '/'
app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)

# Database Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')

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
    template_id = db.Column(db.Integer, db.ForeignKey('task_template.id'), nullable=False)

# Association table for task dependencies
task_dependencies = db.Table(
    'task_dependencies',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('dependency_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)

# API Schemas
class ProjectSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()

class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str()
    status = fields.Str()
    due_date = fields.Date()
    project_id = fields.Int(required=True)
    dependencies = fields.List(fields.Int())

# Blueprint for API
blp = Blueprint('tasks', __name__, description='Operations on tasks and projects')

# API Routes
@blp.route('/projects')
class ProjectList(Resource):
    @blp.response(200, ProjectSchema(many=True))
    def get(self):
        """Get all projects"""
        return Project.query.all()

    @blp.arguments(ProjectSchema)
    @blp.response(201, ProjectSchema)
    def post(self, new_project):
        """Create a new project"""
        project = Project(**new_project)
        db.session.add(project)
        db.session.commit()
        return project

@blp.route('/projects/<int:project_id>')
class ProjectResource(Resource):
    @blp.response(200, ProjectSchema)
    def get(self, project_id):
        """Get a project by ID"""
        project = Project.query.get_or_404(project_id)
        return project

    @blp.arguments(ProjectSchema)
    @blp.response(200, ProjectSchema)
    def put(self, update_data, project_id):
        """Update a project"""
        project = Project.query.get_or_404(project_id)
        project.name = update_data.get('name', project.name)
        project.description = update_data.get('description', project.description)
        db.session.commit()
        return project

    @blp.response(204)
    def delete(self, project_id):
        """Delete a project"""
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return '', 204

@blp.route('/projects/<int:project_id>/tasks')
class TaskList(Resource):
    @blp.response(200, TaskSchema(many=True))
    def get(self, project_id):
        """Get all tasks for a project"""
        return Task.query.filter_by(project_id=project_id).all()

    @blp.arguments(TaskSchema)
    @blp.response(201, TaskSchema)
    def post(self, new_task, project_id):
        """Create a new task for a project"""
        # Validate project exists
        project = Project.query.get_or_404(project_id)

        # Create the task
        task = Task(project_id=project_id, **new_task)

        # Handle dependencies
        if 'dependencies' in new_task:
            for dependency_id in new_task['dependencies']:
                dependency = Task.query.get(dependency_id)
                if dependency:
                    task.dependencies.append(dependency)

        db.session.add(task)
        db.session.commit()
        return task

@blp.route('/tasks/<int:task_id>')
class TaskResource(Resource):
    @blp.response(200, TaskSchema)
    def get(self, task_id):
        """Get a task by ID"""
        task = Task.query.get_or_404(task_id)
        return task

    @blp.arguments(TaskSchema)
    @blp.response(200, TaskSchema)
    def put(self, update_data, task_id):
        """Update a task"""
        task = Task.query.get_or_404(task_id)
        task.title = update_data.get('title', task.title)
        task.description = update_data.get('description', task.description)
        task.status = update_data.get('status', task.status)
        task.due_date = update_data.get('due_date', task.due_date)

        # Update dependencies
        if 'dependencies' in update_data:
            task.dependencies = []
            for dependency_id in update_data['dependencies']:
                dependency = Task.query.get(dependency_id)
                if dependency:
                    task.dependencies.append(dependency)

        db.session.commit()
        return task

    @blp.response(204)
    def delete(self, task_id):
        """Delete a task"""
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return '', 204

# Register the blueprint
api.register_blueprint(blp)

# Frontend Routes
@app.route("/")
def index():
    """Render the homepage with all projects"""
    projects = Project.query.all()
    return render_template("index.html", projects=projects)

@app.route("/add_template", methods=["GET", "POST"])
def add_template():
    """Add a new task template"""
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
        flash('Template created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template("add_template.html")

@app.route("/apply_template/<int:project_id>", methods=["GET", "POST"])
def apply_template(project_id):
    """Apply a task template to a project"""
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
        flash('Template applied successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))

    return render_template("apply_template.html", project_id=project_id, templates=templates)

@app.route("/add_project", methods=["GET", "POST"])
def add_project():
    """Add a new project"""
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        new_project = Project(name=name, description=description)
        db.session.add(new_project)
        db.session.commit()
        flash('Project added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template("add_project.html")

@app.route("/add_project_with_tasks", methods=["GET", "POST"])
def add_project_with_tasks():
    """Add a new project with tasks"""
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

@app.route("/add_task/<int:project_id>", methods=["GET", "POST"])
def add_task(project_id):
    """Add a new task to a project"""
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
                flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
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
        flash('Task added successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))

    return render_template("add_task.html", project_id=project_id, tasks=tasks)

@app.route("/project_detail/<int:project_id>")
def project_detail(project_id):
    """Render the project detail page with tasks"""
    project = Project.query.get_or_404(project_id)
    return render_template("project_detail.html", project=project)

@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    """Edit an existing task"""
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
                flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
                return redirect(url_for('edit_task', task_id=task_id))

        # Update dependencies
        task.dependencies = []
        for dependency_id in dependencies:
            dependency = Task.query.get(dependency_id)
            if dependency:
                task.dependencies.append(dependency)

        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('project_detail', project_id=task.project_id))

    return render_template("edit_task.html", task=task, tasks=tasks)

@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id

    # Remove the task from the dependencies of other tasks
    for dependent_task in task.dependents:
        dependent_task.dependencies.remove(task)

    # Delete the task
    db.session.delete(task)
    db.session.commit()

    flash('Task deleted successfully!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

@app.route("/complete_task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    """Mark a task as complete"""
    task = Task.query.get_or_404(task_id)
    project = Project.query.get_or_404(task.project_id)

    # Check if all dependencies are completed
    for dependency in task.dependencies:
        if dependency.status != 'Done':
            flash(f'Cannot complete task "{task.title}" because dependency "{dependency.title}" is not done.', 'error')
            return redirect(url_for('project_detail', project_id=task.project_id))

    task.status = "Done"
    db.session.commit()
    flash('Task marked as done!', 'success')
    return redirect(url_for('project_detail', project_id=task.project_id))

@app.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    """Edit an existing project"""
    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        project.name = request.form['name']
        project.description = request.form['description']
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template("edit_project.html", project=project)

@app.route("/delete_project/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    """Delete a project"""
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('index'))

# CLI command to initialize the database
@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    db.create_all()
    print("Database initialized.")

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
