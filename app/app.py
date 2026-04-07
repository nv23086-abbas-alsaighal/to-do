from flask import Flask, request, jsonify, render_template
import json
import os
import re

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


def normalize_tags(raw_tags):
    if raw_tags is None:
        return []
    if isinstance(raw_tags, str):
        items = [part.strip() for part in raw_tags.split(',')]
    elif isinstance(raw_tags, list):
        items = [str(part).strip() for part in raw_tags]
    else:
        items = [str(raw_tags).strip()]

    cleaned = []
    for item in items:
        lowered = item.lower()
        lowered = re.sub(r'\s+', ' ', lowered)
        lowered = re.sub(r'[^a-z0-9\-_ ]', '', lowered).strip()
        if lowered and lowered not in cleaned:
            cleaned.append(lowered)
    return cleaned


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
        if 'tags' not in t:
            t['tags'] = []
        else:
            t['tags'] = normalize_tags(t.get('tags'))
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
    tag = request.args.get('tag')
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
    if tag:
        target = normalize_tags([tag])
        if target:
            needle = target[0]
            tasks = [t for t in tasks if needle in normalize_tags(t.get('tags', []))]
    if sort == 'due':
        tasks = sorted(tasks, key=lambda x: x.get('due_date') or '')
    elif sort == 'created':
        tasks = sorted(tasks, key=lambda x: x.get('created_at') or 0)
    return jsonify(tasks)


@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    data = request.get_json() or request.form
    name = data.get('name') or data.get('task')
    description = data.get('description', '')
    priority = int(data.get('priority') or 0)
    due_date = data.get('due_date') or None
    tags = normalize_tags(data.get('tags', []))
    if not name:
        return jsonify({'error': 'Missing task name'}), 400
    tasks = load_tasks()
    next_id = max([t['id'] for t in tasks], default=0) + 1
    task = {'id': next_id, 'name': name, 'description': description, 'priority': priority, 'due_date': due_date, 'completed': False, 'created_at': next_id, 'tags': tags}
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


@app.route('/api/tasks/stats', methods=['GET'])
def api_task_stats():
    tasks = load_tasks()
    total = len(tasks)
    completed = len([t for t in tasks if t.get('completed')])
    overdue = len([t for t in tasks if t.get('due_date') and t.get('due_date') < str(__import__('datetime').date.today()) and not t.get('completed')])
    return jsonify({'total': total, 'completed': completed, 'overdue': overdue})


@app.route('/api/tasks/<int:task_id>', methods=['PUT', 'PATCH'])
def api_update_task(task_id):
    data = request.get_json() or request.form
    tasks = load_tasks()

    for task in tasks:
        if task['id'] == task_id:
            if 'name' in data or 'task' in data:
                task['name'] = data.get('name') or data.get('task')
            if 'description' in data:
                task['description'] = data.get('description')
            if 'priority' in data:
                task['priority'] = int(data.get('priority') or 0)
            if 'due_date' in data:
                task['due_date'] = data.get('due_date') or None
            if 'completed' in data:
                task['completed'] = bool(data.get('completed'))
            if 'tags' in data:
                task['tags'] = normalize_tags(data.get('tags'))

            save_tasks(tasks)
            return jsonify(task), 200

    return jsonify({'error': 'Task not found'}), 404


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    return jsonify(tasks)


@app.route('/api/tags', methods=['GET'])
def api_get_tags():
    tasks = load_tasks()
    tags = sorted({tag for task in tasks for tag in normalize_tags(task.get('tags', []))})
    return jsonify(tags)


@app.route('/api/tasks/<int:task_id>/tags', methods=['POST'])
def api_add_tag(task_id):
    data = request.get_json() or request.form
    raw_tag = data.get('tag')
    tags = normalize_tags([raw_tag])
    if not tags:
        return jsonify({'error': 'Invalid tag'}), 400

    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            current = normalize_tags(task.get('tags', []))
            if tags[0] not in current:
                current.append(tags[0])
            task['tags'] = current
            save_tasks(tasks)
            return jsonify(task)

    return jsonify({'error': 'Task not found'}), 404


@app.route('/api/tasks/<int:task_id>/tags/<path:tag_name>', methods=['DELETE'])
def api_remove_tag(task_id, tag_name):
    tags = normalize_tags([tag_name])
    if not tags:
        return jsonify({'error': 'Invalid tag'}), 400

    target = tags[0]
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['tags'] = [tag for tag in normalize_tags(task.get('tags', [])) if tag != target]
            save_tasks(tasks)
            return jsonify(task)

    return jsonify({'error': 'Task not found'}), 404


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
 