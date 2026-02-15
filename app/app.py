from flask import Flask, request, jsonify, render_template
import json
import os

# Import version: when running as a script the package name may not be available,
# so try both package and local imports and fall back to a default.
try:
    from app.version import __version__
except Exception:
    try:
        from version import __version__
    except Exception:
        __version__ = '0.0.0'

app = Flask(__name__)

DATA_FILE = os.path.join(app.root_path, 'todo.json')


def load_tasks():
    try:
        with open(DATA_FILE, 'r') as f:
            tasks = json.load(f)
    except FileNotFoundError:
        tasks = []
    return tasks


def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)


@app.route('/')
def index():
    tasks = load_tasks()
    return render_template('index.html', tasks=tasks)


@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    return jsonify(load_tasks())


@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    data = request.get_json() or request.form
    name = data.get('name') or data.get('task')
    if not name:
        return jsonify({'error': 'Missing task name'}), 400
    tasks = load_tasks()
    next_id = max([t['id'] for t in tasks], default=0) + 1
    task = {'id': next_id, 'name': name, 'completed': False}
    tasks.append(task)
    save_tasks(tasks)
    return jsonify(tasks)


@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
def api_toggle_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task.get('completed', False)
            break
    save_tasks(tasks)
    return jsonify(tasks)


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    return jsonify(tasks)


@app.route('/api/tasks/clear_completed', methods=['POST'])
def api_clear_completed():
    tasks = load_tasks()
    tasks = [t for t in tasks if not t.get('completed', False)]
    save_tasks(tasks)
    return jsonify(tasks)


@app.route('/version', methods=['GET'])
def version():
    return jsonify({'version': __version__})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
 