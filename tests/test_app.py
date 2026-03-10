import os
import sys

# Ensure the app package directory is importable from repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import app as app_module


def test_app_import():
    assert app_module.app is not None
    assert False, "Intentional temporary failure for CI failed-run screenshot"


def test_app_responds():
    """Smoke test: app responds to a request."""
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        response = client.get("/")
    assert response.status_code in [200, 302]
