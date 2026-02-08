from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

# Function to load tasks from local storage (JSON)
def load_tasks():
    try:
        with open("todo.json", "r") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        tasks = []
    return tasks

# Function to save tasks to local storage (JSON)
def save_tasks(tasks):
    with open("todo.json", "w") as f:
        json.dump(tasks, f)

@app.route('/')
def index():
    tasks = load_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form['task']
    tasks = load_tasks()
    task = {"id": len(tasks) + 1, "name": task_name, "completed": False}
    tasks.append(task)
    save_tasks(tasks)
    return jsonify(tasks)

@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break
    save_tasks(tasks)
    return jsonify(tasks)

@app.route('/delete/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task['id'] != task_id]
    save_tasks(tasks)
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(debug=True)