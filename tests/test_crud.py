import os
import sys

import pytest

# Ensure the app package directory is importable from repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import app as app_module


@pytest.fixture
def client(tmp_path):
    data_file = tmp_path / "todo-test.json"
    data_file.write_text("[]", encoding="utf-8")

    app_module.app.config["TESTING"] = True
    app_module.DATA_FILE = str(data_file)

    with app_module.app.test_client() as test_client:
        yield test_client


def test_create_task(client):
    # Arrange
    payload = {"name": "Buy milk", "description": "2 liters"}

    # Act
    create_resp = client.post("/api/tasks", json=payload)

    # Assert
    assert create_resp.status_code == 200
    created_list = create_resp.get_json()
    assert any(task["name"] == "Buy milk" for task in created_list)

    read_resp = client.get("/api/tasks")
    assert read_resp.status_code == 200
    names = [task["name"] for task in read_resp.get_json()]
    assert "Buy milk" in names


def test_update_task(client):
    # Arrange
    create_resp = client.post("/api/tasks", json={"name": "Old title"})
    assert create_resp.status_code == 200
    task_id = create_resp.get_json()[-1]["id"]

    # Act
    update_resp = client.put(
        f"/api/tasks/{task_id}",
        json={"name": "New title", "description": "Updated details", "priority": 2},
    )

    # Assert
    assert update_resp.status_code == 200
    updated_task = update_resp.get_json()
    assert updated_task["name"] == "New title"
    assert updated_task["priority"] == 2

    read_resp = client.get("/api/tasks")
    assert read_resp.status_code == 200
    tasks = read_resp.get_json()
    assert any(task["name"] == "New title" for task in tasks)
    assert not any(task["name"] == "Old title" for task in tasks)


def test_delete_task(client):
    # Arrange
    create_resp = client.post("/api/tasks", json={"name": "To be deleted"})
    assert create_resp.status_code == 200
    task_id = create_resp.get_json()[-1]["id"]

    # Act
    delete_resp = client.delete(f"/api/tasks/{task_id}")

    # Assert
    assert delete_resp.status_code == 200

    read_resp = client.get("/api/tasks")
    assert read_resp.status_code == 200
    names = [task["name"] for task in read_resp.get_json()]
    assert "To be deleted" not in names


def test_tags_assign_filter_and_remove(client):
    create_resp = client.post("/api/tasks", json={"name": "Tagged task"})
    task_id = create_resp.get_json()[-1]["id"]

    add_tag_resp = client.post(f"/api/tasks/{task_id}/tags", json={"tag": "Work"})
    assert add_tag_resp.status_code == 200
    assert "work" in add_tag_resp.get_json()["tags"]

    filtered_resp = client.get("/api/tasks?tag=work")
    assert filtered_resp.status_code == 200
    filtered = filtered_resp.get_json()
    assert len(filtered) == 1
    assert filtered[0]["id"] == task_id

    remove_tag_resp = client.delete(f"/api/tasks/{task_id}/tags/work")
    assert remove_tag_resp.status_code == 200
    assert "work" not in remove_tag_resp.get_json()["tags"]


def test_comments_crud_and_sanitization(client):
    create_resp = client.post("/api/tasks", json={"name": "Task with comments"})
    task_id = create_resp.get_json()[-1]["id"]

    add_comment_resp = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"body": "<script>alert('x')</script> nice"},
    )
    assert add_comment_resp.status_code == 201
    comment = add_comment_resp.get_json()
    assert "<script>" not in comment["body"]

    list_comments_resp = client.get(f"/api/tasks/{task_id}/comments")
    assert list_comments_resp.status_code == 200
    comments = list_comments_resp.get_json()
    assert len(comments) == 1
    assert comments[0]["id"] == comment["id"]

    delete_comment_resp = client.delete(f"/api/tasks/{task_id}/comments/{comment['id']}")
    assert delete_comment_resp.status_code == 200
    assert delete_comment_resp.get_json() == []


def test_paginated_list_response(client):
    for idx in range(6):
        client.post("/api/tasks", json={"name": f"Task {idx}"})

    page_resp = client.get("/api/tasks?page=2&per_page=2")
    assert page_resp.status_code == 200

    data = page_resp.get_json()
    assert set(data.keys()) == {"items", "page", "per_page", "total", "pages"}
    assert data["page"] == 2
    assert data["per_page"] == 2
    assert data["total"] == 6
    assert data["pages"] == 3
    assert len(data["items"]) == 2
