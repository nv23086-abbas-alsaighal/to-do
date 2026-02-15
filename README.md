# To-Do App

A simple Flask-based to-do application for managing tasks.

## Installation

```bash
pip install -r requirements.txt
```

## Running the App

```bash
cd app
python app.py
```

Then visit `http://localhost:5000` in your browser.

## Features

- Add new tasks
- Mark tasks as complete/incomplete
- Delete tasks
- Tasks persist in JSON format

## Docker / Container

Build the image locally:

```bash
docker build -t youruser/todo:latest .
```

Or use the helper script (set `DOCKERHUB_REPO=owner/repo`):

```bash
DOCKERHUB_REPO=youruser/todo ./scripts/push_to_docker.sh latest
```

To push to Docker Hub you must be logged in. Example:

```bash
docker login
docker push youruser/todo:latest
```

Notes:
- The container serves the Flask app on port `5000`.
- Persisted tasks are stored in `/app/todo.json` inside the image build context; bind-mount a host file to persist across containers.

## Versioning

- **Current version:** Read from the top-level `VERSION` file.
- **Endpoint:** GET `/version` returns JSON `{ "version": "X.Y.Z" }`.
- **Bump script:** Use `./scripts/bump_version.py [major|minor|patch]` to update `VERSION`.

Example:

```bash
./scripts/bump_version.py patch
cat VERSION
```