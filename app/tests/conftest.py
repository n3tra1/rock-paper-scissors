import pytest
from starlette.testclient import TestClient

from app.main import create_app


@pytest.fixture(scope="module")
def test_app():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
