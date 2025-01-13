# Flask Task Manager

A simple yet effective task and project management application built with Flask. This app allows users to register, log in, create projects, and manage tasks within those projects. It includes features like task status tracking, due dates, and user authentication.

---

## **Features**

1. **User Authentication**:
   - Register a new account.
   - Log in and log out securely.
   - Password hashing for security.

2. **Project Management**:
   - Create, edit, and delete projects.
   - Each project is associated with the logged-in user.

3. **Task Management**:
   - Add, edit, and delete tasks within a project.
   - Set task status (`To Do`, `In Progress`, `Done`).
   - Add due dates to tasks.

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
- **Authentication**: Flask-Login
- **Password Hashing**: Werkzeug Security
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

### **1. Register a New User**
- Navigate to the **Register** page.
- Enter a username and password.
- Click **Register** to create your account.

### **2. Log In**
- Navigate to the **Login** page.
- Enter your username and password.
- Click **Login** to access your dashboard.

### **3. Create a Project**
- Click **Add New Project** on the dashboard.
- Enter a name and description for the project.
- Click **Add Project** to save.

### **4. Add Tasks to a Project**
- Click on a project to view its details.
- Click **Add New Task**.
- Enter the task title, description, status, and due date.
- Click **Add Task** to save.

### **5. Edit or Delete Tasks**
- On the project detail page, click **Edit** or **Delete** next to a task to modify or remove it.

### **6. Mark Tasks as Done**
- On the project detail page, click **Mark as Done** to update the task status.

### **7. Edit or Delete Projects**
- On the dashboard, click **Edit** or **Delete** next to a project to modify or remove it.

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
│   ├── edit_project.html
│   ├── edit_task.html
│   ├── index.html
│   ├── login.html
│   ├── project_detail.html
│   └── register.html
└── tasks.db                # SQLite database file
```

---

## **Database Schema**

### **User Table**
- `id`: Primary key (Integer)
- `username`: Unique username (String)
- `password_hash`: Hashed password (String)

### **Project Table**
- `id`: Primary key (Integer)
- `name`: Project name (String)
- `description`: Project description (String)
- `user_id`: Foreign key linking to the `User` table (Integer)

### **Task Table**
- `id`: Primary key (Integer)
- `title`: Task title (String)
- `description`: Task description (String)
- `status`: Task status (`To Do`, `In Progress`, `Done`) (String)
- `due_date`: Task due date (Date)
- `project_id`: Foreign key linking to the `Project` table (Integer)

---

## **Customization**

### **1. Change the Database**
To use a different database (e.g., PostgreSQL), update the `SQLALCHEMY_DATABASE_URI` in `app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/task_manager'
```

### **2. Add New Features**
- **Task Filtering**: Add a filter to view tasks by status.
- **Email Notifications**: Send reminders for tasks with approaching due dates.
- **User Roles**: Implement admin and regular user roles.

---

## **Deployment**

### **Deploy to Render**
1. Push your code to GitHub.
2. Sign up at [Render](https://render.com/).
3. Create a new web service and connect your GitHub repository.
4. Set environment variables:
   - `FLASK_APP=app.py`
   - `FLASK_ENV=production`
5. Deploy the app.

---

## **Contributing**

Contributions are welcome! Follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Acknowledgments**

- Flask Documentation: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- SQLAlchemy Documentation: [https://docs.sqlalchemy.org/](https://docs.sqlalchemy.org/)
- Flask-Login Documentation: [https://flask-login.readthedocs.io/](https://flask-login.readthedocs.io/)

---

Enjoy managing your tasks with Flask Task Manager! 🚀