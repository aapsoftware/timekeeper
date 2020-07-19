import logging
import sqlalchemy
import app.error as error
import datetime
import re
import flask_jwt_extended
from app.storage.db import db
from app.storage.timezones import TimeZones
from app.storage.user_details import UserDetails
from app.storage.user_roles import UserRoles, UserRolesEnum
from app.storage.user_timezones import UserTimeZones
from app.storage.user_token import RevokedUserTokens

log = logging.getLogger(__name__)

def get_user_roles():
    '''get all user roles'''
    user_roles = UserRoles.get_all()
    return {'data': user_roles}

def get_user_role(role):
    '''get user role'''
    user_role = UserRoles.get(role)
    if user_role is None:
        raise error.RecordNotFoundError('User role not found')
    return user_role

def create_user_role(role, permissions):
    '''create new user role'''
    log.error(f'{permissions} ,{UserRolesEnum.values()}')

    if not role or not permissions:
        log.error(f'invalid input: {role}, {permissions}')
        raise ValueError('Invalid input values!')

    if not isinstance(permissions, list):
        raise ValueError('Invalid permissions format: list expected')

    invalid_perm = [x for x in permissions if x not in UserRolesEnum.values()]
    if invalid_perm:
            log.error(f"Invalid perimissions requested:{invalid_perm}. Allowed values: {UserRolesEnum.values()}")
            raise ValueError('Invalid permission value requested')

    new_user_role = UserRoles(role=role, permissions=','.join(permissions))

    try:
        db.session.add(new_user_role)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        raise error.StorageErrorConflict('User role already exists')
    except sqlalchemy.exc.SQLAlchemyError as ex:
        db.session.rollback()
        log.error(f'Could not create user role: {ex}')
        raise error.StorageError('Could not reate user role!')

    ret_value = new_user_role.to_dict()
    log.info(f'New user role {ret_value} successfully added')
    return ret_value


def delete_user_role(role):
    '''delete user role'''
    try:
        user_role = get_user_role(role)
        UserRoles.delete(role)
    except sqlalchemy.exc.SQLAlchemyError as ex:
        log.error(f'Error while deleting user role {ex}')
        raise error.StorageError(f'Error while deleting user role {role}')

    log.info(f'User role {role} deleted')



def get_user_all(req_username, permission):
    '''get all user details depending on user privileges'''
    base_query = db.session.query(UserDetails, UserRoles.role).outerjoin(UserRoles, UserRoles.id == UserDetails.role_id)
    if permission == UserRolesEnum.user.value:
        query = base_query.filter(UserDetails.username == req_username)
    elif permission == UserRolesEnum.user_privileged.value:
        query = base_query.filter(UserRoles.permissions.contains(UserRolesEnum.user.value))
    else:
        query = base_query
    try:
        req_list = query.all()
        ret_list = []

        for item in req_list:
            user = item.UserDetails.to_dict()
            user['role'] = item.role
            ret_list.append(user)

        return {'data': ret_list}

    except sqlalchemy.exc.SQLAlchemyError as ex:
        log.error(f'Error while retrieving user details: {ex}')
        raise error.StorageError('Error while retrieving user details')

def _validate_user_request(username, req_username, permission):
    '''checks if the requesting user has the right permissions for the requested action'''
    if not username == req_username:
        if permission == UserRolesEnum.user.value:
            raise error.PermissionsError()
        user_details = UserDetails.get(username)
        if not user_details:
            raise error.RecordNotFoundError(f'username {username} not found')
        if user_details.role_id:
            perm_query = db.session.query(UserRoles.permissions).join(UserDetails, UserRoles.id == UserDetails.role_id)
            perm_query = perm_query.filter(UserDetails.username == username)
            user_perm = perm_query.one_or_none()
            if not user_perm:
                raise error.RecordNotFoundError(f'username {username} not found')
            if ((UserRolesEnum.user_privileged.value in user_perm.permissions or
                UserRolesEnum.user_all.value in user_perm.permissions) and
                not permission == UserRolesEnum.user_all.value):
                raise error.PermissionsError()

def get_user(username, req_username, permission):
    '''get a user details'''
    _validate_user_request(username, req_username, permission)

    query = db.session.query(UserDetails, UserRoles.role).join(UserRoles, UserRoles.id == UserDetails.role_id)
    try:
        query = query.filter(UserDetails.username == username)
        res = query.one_or_none()
        if not res:
            raise error.RecordNotFoundError(f'username {username} not found')
        user = res.UserDetails.to_dict()
        user['role'] = res.role
        return user
    except sqlalchemy.exc.SQLAlchemyError as ex:
        log.error(f'Error while retrieving user details: {ex}')
        raise error.StorageError('Error while retrieving user details')


def _check_email_address_format(email):
    '''
    an valid email address is a string (a subset of ASCII characters)
    separated into two parts by @ symbol, a “personal_info” and a domain
    followed by .domain_type
    e.g. personal_info@domain.net
    '''
    email_regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if not (re.search(email_regex, email)):
        raise error.InvalidFieldFormat('Invalid email address format')

def _check_name_field(name, min_len=6):
    '''
    verify name fields
    '''
    if len(name)<min_len:
        raise error.InvalidFieldFormat(f'Invalid name field format, minimum {min_len} characters required')

def _check_passwd_field(password):
    '''
    verify password field
    '''
    if len(password)<8:
        raise error.InvalidFieldFormat('Invalid password format, minimum 8 characters required')

def create_user(first_name, last_name, username, email, password):
    '''create a new user'''
    if not first_name or not last_name or not username or not email or not password:
        log.error(f'invalid input: {first_name}, {last_name}, {username}, {email}, {password}')
        raise ValueError('Invalid input values!')

    _check_name_field(first_name, 3)
    _check_name_field(last_name, 3)
    _check_name_field(username)
    _check_email_address_format(email)
    _check_passwd_field(password)

    user = UserDetails.get(username)
    if user:
        raise error.StorageErrorConflict('username already exists')

    user_email = db.session.query(UserDetails).filter_by(email=email).one_or_none()
    if user_email:
        raise error.StorageErrorConflict('email already registered')

    #user_role = get_user_role(role)

    new_user = UserDetails(
        first_name=first_name, last_name=last_name, username=username,
        email=email, password=UserDetails.generate_hash(password)
    )

    try:
        db.session.add(new_user)
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as ex:
        db.session.rollback()
        log.error(f'Could not reate user {username}: {ex}')
        raise error.StorageError(f'Could not add user {username}!')

    log.info(f'User {username} created')

    user_info = new_user.to_dict()
    return user_info

def update_user(username, req_username, permission, **kwargs):
    '''update an existing user'''
    _validate_user_request(username, req_username, permission)

    first_name = kwargs.get('first_name')
    last_name = kwargs.get('last_name')
    email = kwargs.get('email')
    password = kwargs.get('password')
    role = kwargs.get('role')

    role_id = None
    if role:
        if not permission == UserRolesEnum.user_all.value:
            raise error.PermissionsError('insufficient permissions to update role')
        role_details = UserRoles.get(role)
        if not role_details:
            raise error.RecordNotFoundError(f'role {role} not found')
        role_id = role_details['id']

    if email:
        _check_email_address_format(email)

    user = UserDetails.get(username)
    if not user:
        raise error.RecordNotFoundError(f'username {username} not found')

    changed = False
    try:
        if role_id and user.role_id != role_id:
            user.role_id = role_id
            changed = True

        if first_name and user.first_name != first_name:
            _check_name_field(first_name, 3)
            user.first_name = first_name
            changed = True

        if last_name and user.last_name != last_name:
            _check_name_field(last_name, 3)
            user.last_name = last_name
            changed = True

        if email and user.email != email:
            _check_email_address_format(email)
            user.email = email
            changed = True

        if password and not UserDetails.verify_hash(password, user.password):
            _check_passwd_field(password)
            user.password = UserDetails.generate_hash(password)
            changed = True

        if changed:

            db.session.add(user)
            db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as ex:
        db.session.rollback()
        log.error(f'Could not update user {username}: {ex}')
        raise error.StorageError(f'Could not update user {username}!')
    except Exception as ex:
        db.session.rollback()
        log.error(f'Could not update user {username}: {ex}')
        raise

    log.info(f'User {username} updated')

def delete_user(username, req_username, permission):
    '''delete a user'''
    try:
        user = get_user(username, req_username, permission)
        UserDetails.delete(username)
    except sqlalchemy.exc.SQLAlchemyError as ex:
        log.error(f'Error while deleting user {username} {ex}')
        raise error.StorageError(f'Error while deleting user {username}')

    log.info(f'User {username} deleted')


def enable_user(username, enable_value):
    '''enable/disble an existing user'''
    user = UserDetails.get(username)
    if not user:
        raise error.RecordNotFoundError(f'username {username} not found')

    changed = False
    try:
        if user.enabled != enable_value:
            user.enabled = enable_value
            changed = True

        if changed:
            db.session.add(user)
            db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as ex:
        db.session.rollback()
        log.error(f'Could not update user {username}: {ex}')
        raise error.StorageError(f'Could not update user {username}!')
    except Exception as ex:
        db.session.rollback()
        log.error(f'Could not update user {username}: {ex}')
        raise

    enabled_str = 'enabled' if enable_value else 'disabled'
    log.info(f'User {username} {enabled_str}')

def get_timezone_all():
    '''get all timezones'''
    try:
        ret_list = TimeZones.get_all()
        return {'data': ret_list}
    except sqlalchemy.exc.SQLAlchemyError as ex:
        log.error(f'Error while retrieving timezones: {ex}')
        raise error.StorageError(f'Error while retrieving timezones')

def get_user_timezone_all(username):
    '''get all timezones for a user'''
    user = UserDetails.get(username)
    if not user:
        raise error.RecordNotFoundError(f'username {username} not found')

    query = db.session.query(UserTimeZones, TimeZones, UserDetails.username)\
            .join(UserDetails, UserTimeZones.user_id == UserDetails.id)\
            .join(TimeZones, UserTimeZones.timezone_id == TimeZones.id)\
            .filter(UserDetails.username == username)

    try:
        req_list = query.all()
        ret_list = []

        for item in req_list:
            tz = item.TimeZones.to_dict()
            tz.update(item.UserTimeZones.to_dict())
            tz['username'] = item.username
            ret_list.append(tz)

        return {'data': ret_list}

    except sqlalchemy.exc.SQLAlchemyError as ex:
        log.error(f'Error while retrieving user timezones: {ex}')
        raise error.StorageError(f'Error while retrieving user {username} timezones')


def _get_timezone_by_username_and_name(username, name):
    query = db.session.query(UserTimeZones).join(UserDetails, UserTimeZones.user_id == UserDetails.id)
    query = query.filter(UserDetails.username == username).filter(UserTimeZones.name == name)
    return query.one_or_none()

def create_user_timezone(username, name, timezone_id):
    '''create a new user timezone'''
    if not name or not timezone_id:
        log.error(f'invalid input: {name}, {timezone_id}')
        raise ValueError('Invalid input values!')

    user = UserDetails.get(username)
    if not user:
        raise error.RecordNotFoundError(f'username {username} not found')

    timezone = TimeZones.get(timezone_id)
    if not timezone:
        log.error(f'timezone {timezone_id} not found')
        raise error.RecordNotFoundError(f'requested timezone not found')

    res = _get_timezone_by_username_and_name(username, name)
    if res:
        raise error.StorageErrorConflict(f'timezone {name} already exists')

    new_user_timezone = UserTimeZones(
        user_id=user.id, name=name, timezone_id=timezone_id
    )

    try:
        db.session.add(new_user_timezone)
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as ex:
        db.session.rollback()
        log.error(f'Could not create timezone {name} for {username}: {ex}')
        raise error.StorageError(f'Could not add timezone {name} for user {username}!')

    log.info(f'User {username} created')
    return new_user_timezone

def get_user_timezone(username, name):
    '''get a user timezone'''
    user = UserDetails.get(username)
    if not user:
        raise error.RecordNotFoundError(f'username {username} not found')

    query = db.session.query(UserTimeZones, TimeZones)\
            .join(UserDetails, UserTimeZones.user_id == UserDetails.id)\
            .join(TimeZones, UserTimeZones.timezone_id == TimeZones.id)\
            .filter(UserDetails.username == username)\
            .filter(UserTimeZones.name == name)

    res = query.one_or_none()
    if not res:
        raise error.RecordNotFoundError(f'user {username} timezone {name} not found')

    timezone = res.TimeZones.to_dict()
    timezone.update(res.UserTimeZones.to_dict())

    return timezone

def update_user_timezone(username, tz_name, **kwargs):
    '''update a user timezone'''
    new_name = kwargs.get('name')
    timezone_id = kwargs.get('timezone_id')

    user = UserDetails.get(username)
    if not user:
        raise error.RecordNotFoundError(f'username {username} not found')

    timezone = _get_timezone_by_username_and_name(username, tz_name)
    if not timezone:
        raise error.RecordNotFoundError(f'timezone {tz_name} not found')

    changed = False

    if new_name and timezone.name != new_name:
        tz = _get_timezone_by_username_and_name(username, new_name)
        if tz:
            raise error.StorageErrorConflict(f'timezone {new_name} already exists')

        timezone.name = new_name
        changed = True

    if timezone_id and timezone.timezone_id != timezone_id:
        timezone.timezone_id = timezone_id
        changed = True

    if changed:
        try:
            db.session.add(timezone)
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as ex:
            db.session.rollback()
            log.error(f'Could not update timezone {tz_name}: {ex}')
            raise error.StorageError(f'Could not update timezone {tz_name}!')

    log.info(f'timezone {tz_name} updated user {username}')


def delete_user_timezone(username, name):
    '''delete a user timezone'''
    user = UserDetails.get(username)
    if not user:
        raise error.RecordNotFoundError(f'username {username} not found')

    timezone = _get_timezone_by_username_and_name(username, name)
    if not timezone:
        raise error.RecordNotFoundError(f'timezone {tz_name} not found')
    log.error(f'deleteing {timezone}')
    try:
        db.session.delete(timezone)
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as ex:
        db.session.rollback()
        log.error(f'Error while deleting timezone {name}: {ex}')
        raise error.StorageError(f'Error while deleting timezone {name}')

    log.info(f'timezone {name} deleted for user {username}')


def authenticate_user(username, passwd):
    """
    generates jwt token for user
    """
    query = db.session.query(UserDetails, UserRoles).outerjoin(UserRoles, UserRoles.id == UserDetails.role_id)

    user = None
    if username is not None:
        query = query.filter(UserDetails.username == username)
        res = query.one_or_none()

        if res and ( not res.UserDetails.enabled or not res.UserDetails.role_id ):
            raise error.AuthError('User Account is not yet active, please contact support')

        if not(res and UserDetails.verify_hash(passwd, res.UserDetails.password)):
            raise error.AuthError('invalid user credentials')

        user = res.UserRoles.to_dict()
        user.update(res.UserDetails.to_dict())
    else:
        raise error.AuthError("invalid username format")

    access_token = flask_jwt_extended.create_access_token(identity=user)
    log.info(f'created JWT access tokens for user {username}: {access_token}')

    return {'access_token': access_token}

def revoke_token(jti):
    """
    revoke a token
    """
    revoked_token = RevokedUserTokens(jti=jti)
    try:
        db.session.add(revoked_token)
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as ex:
        db.session.rollback()
        log.error(f'Could not add token JTI {jti} to revoked tokens: {ex}')
        raise error.StorageError(f'problem revoking token')

    log.info(f'token {jti} revoked')