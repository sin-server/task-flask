# Flask Task Manager

A simple yet effective task and project management application built with Flask. This app allows users to create projects, manage tasks within those projects, and use task templates for recurring workflows. It includes features like task status tracking, due dates, task dependencies, and task templates.

---

## **Features**

1. **Project Management**:
   - Create, edit, and delete projects.
   - Each project can have multiple tasks.

2. **Task Management**:
   - Add, edit, and delete tasks within a project.
   - Set task status (`To Do`, `In Progress`, `Done`).
   - Add due dates to tasks.
   - Define task dependencies (e.g., Task B cannot start until Task A is completed).

3. **Task Templates**:
   - Create reusable task templates for common workflows.
   - Apply templates to projects to automatically generate tasks.

4. **Responsive Design**:
   - Clean and modern UI with responsive CSS for all screen sizes.

5. **Database Integration**:
   - Uses SQLite for data storage.
   - Flask-SQLAlchemy for database management.
   - Flask-Migrate for database schema migrations.

---

## **Technologies Used**

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (with modern styling)
- **Database**: SQLite
- **Database Migrations**: Flask-Migrate

---

## **Getting Started**

### **Prerequisites**

1. **Python 3.12+**: Ensure Python is installed on your system.
2. **Pip**: Python package manager.
3. **Virtual Environment (Optional)**: Recommended for isolating dependencies.

### **Installation**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/flask-task-manager.git
   cd flask-task-manager
   ```

2. **Set Up a Virtual Environment (Optional)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**:
   ```bash
   flask init-db
   ```

5. **Run the Application**:
   ```bash
   flask run
   ```

6. **Access the App**:
   Open your browser and navigate to `http://127.0.0.1:5000`.

---

## **Usage**

### **1. Create a Project**
- Click **Add New Project** on the dashboard.
- Enter a name and description for the project.
- Click **Add Project** to save.

### **2. Add Tasks to a Project**
- Click on a project to view its details.
- Click **Add New Task**.
- Enter the task title, description, status, and due date.
- Click **Add Task** to save.

### **3. Edit or Delete Tasks**
- On the project detail page, click **Edit** or **Delete** next to a task to modify or remove it.

### **4. Mark Tasks as Done**
- On the project detail page, click **Mark as Done** to update the task status.

### **5. Define Task Dependencies**
- When adding or editing a task, select dependencies from the list of existing tasks.
- Tasks cannot be marked as "Done" until their dependencies are completed.

### **6. Create Task Templates**
- Click **Add Task Template** on the dashboard.
- Enter a name and description for the template.
- Add tasks to the template with titles, descriptions, and due date offsets.
- Click **Submit** to save the template.

### **7. Apply Task Templates**
- On the project detail page, click **Apply Template**.
- Select a template from the list and click **Apply Template**.
- Tasks will be created based on the template.

---

## **Project Structure**

```
flask-task-manager/
├── app.py                  # Main Flask application
├── requirements.txt        # List of dependencies
├── README.md               # Project documentation
├── static/
│   └── main.css            # Custom CSS for styling
├── templates/              # HTML templates
│   ├── add_project.html
│   ├── add_task.html
│   ├── add_template.html
│   ├── apply_template.html
│   ├── edit_project.html
│   ├── edit_task.html
│   ├── index.html
│   ├── project_detail.html
└── tasks.db                # SQLite database file
```

---

## **Database Schema**

### **Project Table**
- `id`: Primary key (Integer)
- `name`: Project name (String)
- `description`: Project description (String)

### **Task Table**
- `id`: Primary key (Integer)
- `title`: Task title (String)
- `description`: Task description (String)
- `status`: Task status (`To Do`, `In Progress`, `Done`) (String)
- `due_date`: Task due date (Date)
- `project_id`: Foreign key linking to the `Project` table (Integer)
- `dependencies`: Many-to-many relationship with other tasks.

### **TaskTemplate Table**
- `id`: Primary key (Integer)
- `name`: Template name (String)
- `description`: Template description (String)

### **TemplateTask Table**
- `id`: Primary key (Integer)
- `title`: Task title (String)
- `description`: Task description (String)
- `status`: Task status (`To Do`, `In Progress`, `Done`) (String)
- `due_date_offset`: Days offset from the project start date (Integer)
- `template_id`: Foreign key linking to the `TaskTemplate` table (Integer)

---

## **Customization**

### **1. Change the Database**
- Modify the `SQLALCHEMY_DATABASE_URI` in `app.py` to use a different database system like PostgreSQL or MySQL.

### **2. Add New Features**
- Extend the app with additional features like user authentication, collaboration, or integrations with external tools.

---

## **Contributing**

Contributions are welcome! If you'd like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Acknowledgments**

- Flask for providing a lightweight and flexible web framework.
- SQLAlchemy for simplifying database interactions.
- The open-source community for inspiration and support.
