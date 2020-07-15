import logging
import app.error as err
import flask_jwt_extended
from app.storage.user_roles import UserRolesEnum
from app.storage.user_details import UserDetails

log = logging.getLogger(__name__)

def validate_permissions(required_permission, username=None):
    '''
    checks if user claims have the right permissions
    '''
    identity_mismatch = False
    if username:
        user_identity = flask_jwt_extended.get_jwt_identity()
        if not user_identity == username:
            identity_mismatch = True
        else:
            return

    claims = flask_jwt_extended.get_jwt_claims()
    if required_permission not in claims['permissions']:
        if identity_mismatch:
            log.error(f"unauthorized: user {user_identity} cannot access other users data")
            raise err.PermissionsError()
        else:
            log.error(f"unauthorized: required {required_permission} claims {claims['permissions']}")
            raise err.PermissionsError()


def get_user_permissions():
    user_identity = flask_jwt_extended.get_jwt_identity()
    claims = flask_jwt_extended.get_jwt_claims()
    permission = UserRolesEnum.user.value

    if UserRolesEnum.user_privileged.value in claims['permissions']:
        permission = UserRolesEnum.user_privileged.value
    if UserRolesEnum.user_all.value in claims['permissions']:
        permission = UserRolesEnum.user_all.value

    return user_identity, permission


def check_user_enabled():
    user_identity = flask_jwt_extended.get_jwt_identity()
    user = UserDetails.get(user_identity)
    if not user:
        raise Exception('Could not identify user!')
    if not user.enabled:
        raise err.PermissionsError('Account is diabled; please contact support for further details')