from flask_testing import TestCase
import flask
import os
import app.server as server
from app.app_config import TestingConfig as config
from app.storage.db import db


class BaseTestCase(TestCase):

    def create_app(self):
        app = server.initialize_app(config)
        return app

    def tearDown(self):
        db.session.remove()
        db.drop_all()
