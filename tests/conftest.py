import pytest

from main import app as main_app, db
from populate_db import populate_db


@pytest.fixture(autouse=True)
def app():
    with main_app.app_context():
        db.create_all()
        populate_db()

        yield app
