import logging
import werkzeug.exceptions
import flask_restplus
import flask_jwt_extended
import app.error as err
import jwt

log = logging.getLogger(__name__)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

flask_api = flask_restplus.Api(
    version='1.0',
    title='Timezone Keeper API',
    description='A timezone keeper for everyday use',
    default='timezone',
    default_label='',
    ordered=False,
    authorizations=authorizations,
    ui='/'
)

@flask_api.errorhandler(err.StorageError)
def handle_storage_error(error):
    """Storage Errors"""
    http_status = 400
    if isinstance(error, err.StorageErrorConflict):
        http_status = 409

    if isinstance(error, err.RecordNotFoundError):
        http_status = 404

    return {'error': {'message': str(error)}}, http_status


@flask_api.errorhandler(ValueError)
@flask_api.errorhandler(err.InvalidFieldFormat)
def handle_errors(error):
    """Misc Errors"""
    http_status = 400
    return {'error': {'message': str(error)}}, http_status


@flask_api.errorhandler(err.AuthError)
def handle_auth_errors(error):
    """Auth Errors"""
    http_status = 401
    msg = str(error)
    if (isinstance(error, err.PermissionsError)):
        http_status = 403
        msg = 'unauthorized'
        if str(error):
            msg = str(error)
    return {'error': {'message': msg}}, http_status


@flask_api.errorhandler(jwt.PyJWTError)
def handle_expired_tokens(error):
    '''Handles errors dues to using expired tokens'''
    http_status = 401
    msg = 'invalid access token'
    if (isinstance(error, jwt.ExpiredSignatureError)):
        msg = 'access token has expired'

    return {'error': {'code': http_status, 'message': msg}}, http_status

# @flask_api.errorhandler(jwt.exceptions.InvalidSignatureError)
# def handle_invalid_tokens(error):
#     '''Handles errors dues to using invalid tokens'''
#     http_status = 401
#     return {'error': {'code': http_status, 'message': 'invalid access token'}}, http_status

@flask_api.errorhandler(flask_jwt_extended.exceptions.JWTExtendedException)
def handle_auth_error(error):
    """JWT authentication error"""
    http_status = 401
    if (isinstance(error, flask_jwt_extended.exceptions.JWTDecodeError) or
        isinstance(error, flask_jwt_extended.exceptions.WrongTokenError)):
        http_status = 422
    elif isinstance(error, flask_jwt_extended.exceptions.UserClaimsVerificationError):
        http_status = 400
    return {'error': {'code': http_status, 'message': str(error)}}, http_status

@flask_api.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(error):
    """Invalid Request"""
    return {'error': {'message': str(error)}}, 400


@flask_api.errorhandler(werkzeug.exceptions.NotFound)
def handle_not_found(error):
    """Not Found"""
    return {'error': {'message': str(error)}}, 404


@flask_api.errorhandler
def handle_default_error(error):
    """Internal processing error"""
    log.exception('An unhandled exception occurred. %s', str(error))

    return {'error': {'code': 500, 'message': "An internal error occurred"}}, 500
