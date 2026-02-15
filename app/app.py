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
    # ensure backward compatibility and fill defaults
    normalized = []
    for t in tasks:
        if 'description' not in t:
            t['description'] = ''
        if 'priority' not in t:
            t['priority'] = 0
        if 'due_date' not in t:
            t['due_date'] = None
        if 'created_at' not in t:
            t['created_at'] = t.get('id', 0)
        normalized.append(t)
    tasks = normalized
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
    tasks = load_tasks()
    # basic query/filter support
    q = request.args.get('q')
    status = request.args.get('status')
    priority = request.args.get('priority')
    sort = request.args.get('sort')
    if q:
        ql = q.lower()
        tasks = [t for t in tasks if ql in t.get('name','').lower() or ql in t.get('description','').lower()]
    if status == 'completed':
        tasks = [t for t in tasks if t.get('completed')]
    elif status == 'pending':
        tasks = [t for t in tasks if not t.get('completed')]
    if priority is not None:
        try:
            p = int(priority)
            tasks = [t for t in tasks if int(t.get('priority',0)) == p]
        except Exception:
            pass
    if sort == 'due':
        tasks = sorted(tasks, key=lambda x: x.get('due_date') or '')
    elif sort == 'created':
        tasks = sorted(tasks, key=lambda x: x.get('created_at') or 0)
    return jsonify(tasks)


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
 