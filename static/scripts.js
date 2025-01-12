<form method="POST" action="{{ url_for('delete_project', project_id=project.id) }}" onsubmit="return confirm('Are you sure you want to delete this project?');">
    <button type="submit">Delete</button>
</form>