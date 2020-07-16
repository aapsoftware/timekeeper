"""
Flask RESTPlus API with 3 namespaces
1. User API for managing user details
2. Role API for managing user roles
3. Timezone API for managing user timezones
"""
import logging
import flask_jwt_extended
from flask import Flask, Blueprint, request
from app.rest import flask_api
from app.view.auth_api import ns as auth_ns
from app.view.role_api import ns as role_ns
from app.view.user_api import ns as user_ns
from app.view.timezone_api import ns as timezone_ns
from app.storage.db import db
from app.storage.user_token import RevokedUserTokens
from app.view.utils import check_user_enabled


API_PREFIX = '/api/v1'

log = logging.getLogger(__name__)

class FlaskCfgObject(object):
    def __init__(self, server_cfg):

        # Flask does not work well with 0.0.0.0 being used as domain in SERVER_NAME
        if server_cfg.SERVER_HOST != '0.0.0.0':
            self.SERVER_NAME = '{0}:{1}'.format(server_cfg.SERVER_HOST, server_cfg.SERVER_PORT)
        self.SERVER_HOST_AND_PORT = '{0}:{1}'.format(server_cfg.SERVER_HOST, server_cfg.SERVER_PORT)

        self.RESTPLUS_VALIDATE = server_cfg.RESTPLUS_VALIDATE
        self.RESTPLUS_MASK_SWAGGER = server_cfg.RESTPLUS_MASK_SWAGGER
        self.ERROR_404_HELP = server_cfg.RESTPLUS_ERROR_404_HELP
        self.ERROR_INCLUDE_MESSAGE = server_cfg.RESTPLUS_ERROR_INCLUDE_MESSAGE

        # database location can be overridden in server_cfg
        self.SQLALCHEMY_DATABASE_URI = server_cfg.SQLALCHEMY_DATABASE_URI
        self.SQLALCHEMY_COMMIT_ON_TEARDOWN = True

        # these 2 settings useful for debugging
        self.SQLALCHEMY_ECHO = server_cfg.SQLALCHEMY_ECHO
        self.SQLALCHEMY_TRACK_MODIFICATIONS = server_cfg.SQLALCHEMY_TRACK_MODIFICATIONS

        self.JWT_SECRET_KEY = server_cfg.JWT_SECRET_KEY
        self.JWT_BLACKLIST_ENABLED = True
        self.JWT_BLACKLIST_TOKEN_CHECKS = ['access', ]
        self.JWT_ACCESS_TOKEN_EXPIRES = server_cfg.JWT_ACCESS_TOKEN_EXPIRES

        self.CORS = 'Content-Type'
        self.TIMEZONE_INITIAL_VALUES = server_cfg.TIMEZONE_INITIAL_VALUES
        self.TESTING = server_cfg.TESTING

        # flask uses ENV
        if server_cfg.FLASK_DEBUG:
            self.ENV = 'development'

# callback for create_access_token
# Lets us define the custom claims in access token
def jwt_add_claims_to_access_token(user):
    return {
        'role': user['role'],
        'permissions': user['permissions']
    }

# callback for create_access_token
# Lets us define the identity in access token
def jwt_user_identity_lookup(user):
    return user['username']

# callback for jti blacklist loader
def jwt_check_blacklisted(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedUserTokens.is_blacklisted(jti)


# callback to add CORS headers to each response
def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
            headers = request.headers.get('Access-Control-Request-Headers')
            if headers:
                response.headers['Access-Control-Allow-Headers'] = headers
        return response

def create_app(config):
    """
    Create a Flask app with a registered API and namespaces
    """
    flask_app = Flask('timezone_keeper')
    flask_app.config.from_object(FlaskCfgObject(config))
    blueprint = Blueprint('api', __name__, url_prefix=API_PREFIX)
    flask_api.init_app(blueprint)
    flask_api.add_namespace(auth_ns)
    flask_api.add_namespace(user_ns)
    flask_api.add_namespace(role_ns)
    flask_api.add_namespace(timezone_ns)

    if 'api' not in flask_app.blueprints:
        flask_app.register_blueprint(blueprint)

    log.info('Database path: %s', config.SQLALCHEMY_DATABASE_URI)
    db.init_app(flask_app)

    jwt = flask_jwt_extended.JWTManager(flask_app)
    jwt.user_claims_loader(jwt_add_claims_to_access_token)
    jwt.user_identity_loader(jwt_user_identity_lookup)
    jwt.token_in_blacklist_loader(jwt_check_blacklisted)

    flask_app.after_request(add_cors_headers)

    return flask_app

def init_db(app):
    with app.app_context():
        db.create_all()
        db.session.commit()

def initialize_app(cfg):
    app = create_app(cfg)
    init_db(app)

    return app
