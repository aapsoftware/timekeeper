import flask_restplus
import app.rest as rest

UserRole = rest.flask_api.model('UserRole', {
    'role': flask_restplus.fields.String(description='User Role', example='admin'),
    'permissions': flask_restplus.fields.List(
        flask_restplus.fields.String, skip_none=True, example=['CRUD-records']
    ),
})

UserRolesList = rest.flask_api.model('UserRolesList', {
    'data': flask_restplus.fields.List(flask_restplus.fields.Nested(UserRole, skip_none=True))
})

User = rest.flask_api.model('User', {
    'first_name': flask_restplus.fields.String(required=True, description='first name', example='John'),
    'last_name': flask_restplus.fields.String(required=True, description='last name', example='Doe'),
    'username': flask_restplus.fields.String(required=True, description='username', example='JohnDoe2'),
    'email': flask_restplus.fields.String(required=True, description='user email', example='me@email.com'),
    'role': flask_restplus.fields.String(required=True, description='user role', example='manager'),
    'enabled': flask_restplus.fields.Boolean(required=False, description='User account status', example=True)
})

UserWithPasswd = rest.flask_api.model('UserWithPasswd', {
    'first_name': flask_restplus.fields.String(required=True, description='first name', example='John'),
    'last_name': flask_restplus.fields.String(required=True, description='last name', example='Doe'),
    'username': flask_restplus.fields.String(required=True, description='username', example='JohnDoe2'),
    'email': flask_restplus.fields.String(required=True, description='user email', example='me@email.com'),
    'password': flask_restplus.fields.String(required=True, description='password', example='P@55w0rd!')
})

UserUpdatable = rest.flask_api.model('UserUpdatable', {
    'first_name': flask_restplus.fields.String(required=False, description='first name', example='John'),
    'last_name': flask_restplus.fields.String(required=False, description='last name', example='Doe'),
    'email': flask_restplus.fields.String(required=False, description='user email', example='me@email.com'),
    'password': flask_restplus.fields.String(required=False, description='user password', example='this_is_my_password'),
    'role': flask_restplus.fields.String(required=False, description='user role', example='user'),
})

UserAuth = rest.flask_api.model('UserAuth', {
    'username': flask_restplus.fields.String(required=True, description='username', example='JohnDoe2'),
    'password': flask_restplus.fields.String(required=True, description='password', example='P@55w0rd!')
})

UserData = rest.flask_api.model('UserData', {
    'data': flask_restplus.fields.List(flask_restplus.fields.Nested(User, skip_none=True))
})

Timezone = rest.flask_api.model('Timezone', {
    'name': flask_restplus.fields.String(required=True, description='timezone name', example='GMT'),
    'location': flask_restplus.fields.String(required=True, description='timezone location', example='Europe'),
    'city': flask_restplus.fields.String(required=True, description='city name withing the timezone', example='London'),
    'relative_to_gmt': flask_restplus.fields.String(required=True, description='gmt offset, in hours', example='0:00')
})

Timezone2 = rest.flask_api.model('Timezone2', {
    'id': flask_restplus.fields.Integer(required=True, description='user timezone id', example=1),
    'location': flask_restplus.fields.String(required=True, description='timezone location', example='Europe'),
    'city': flask_restplus.fields.String(required=True, description='city name withing the timezone', example='London'),
    'relative_to_gmt': flask_restplus.fields.String(required=True, description='gmt offset, in hours', example='0:00')
})

UserTimezone = rest.flask_api.model('UserTimezone', {
    'id': flask_restplus.fields.Integer(required=True, description='user timezone id', example=1),
    'name': flask_restplus.fields.String(required=True, description='timezone name', example='GMT'),
    'timezone_id': flask_restplus.fields.Integer(required=True, description='timezone id', example=2)
})

UserTimezoneNoId = rest.flask_api.model('UserTimezoneNoId', {
    'name': flask_restplus.fields.String(required=True, description='timezone name', example='GMT'),
    'timezone_id': flask_restplus.fields.Integer(required=True, description='timezone id', example=2)
})

TimezoneList = rest.flask_api.model('TimezoneList', {
    'data': flask_restplus.fields.List(flask_restplus.fields.Nested(Timezone, skip_none=True))
})

TimezoneList2 = rest.flask_api.model('TimezoneList2', {
    'data': flask_restplus.fields.List(flask_restplus.fields.Nested(Timezone2, skip_none=True))
})