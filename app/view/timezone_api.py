"""
Timezone API
"""
import logging

from flask_restplus import Resource
from app.rest import flask_api
import app.view.serializers as serializers
import app.queries_handler as qh
from flask import request
import flask_restplus
import flask_jwt_extended
from app.storage.user_roles import UserRolesEnum
import app.view.utils as utils

log = logging.getLogger(__name__)

ns = flask_api.namespace('timezone', validate=True, description=__doc__)


@ns.doc(security='apikey')
@ns.route('')
@ns.response(404, 'timezone not found')
@ns.response(200, 'timezone retuned successfully')
class Timezones(Resource):
    @ns.doc('list_timezones')
    @flask_jwt_extended.jwt_required
    @ns.marshal_with(serializers.TimezoneList2, skip_none=True)
    def get(self):
        """Get all timezones"""
        utils.check_user_enabled()
        data = qh.get_timezone_all()
        if not data["data"]:
            return {}, 404
        return data

@ns.doc(security='apikey')
@ns.route('/<username>')
@ns.param('username', 'username')
@ns.response(404, 'User timezone not found')
class UserTimezones(Resource):
    @ns.doc('list_user_timezones')
    @flask_jwt_extended.jwt_required
    @ns.marshal_with(serializers.TimezoneList, skip_none=True)
    @ns.response(200, 'User timezones retuned successfully')
    @ns.response(400, 'Bad request')
    def get(self, username):
        """Get all timezones for a user"""
        utils.check_user_enabled()
        utils.validate_permissions(required_permission=UserRolesEnum.record_all.value, username=username)
        data = qh.get_user_timezone_all(username)
        if not data["data"]:
            return {}, 404
        return data

    @ns.doc('create_new_user_timezone')
    @flask_jwt_extended.jwt_required
    @ns.expect(serializers.UserTimezoneNoId, validate=True)
    @ns.marshal_with(serializers.UserTimezone, skip_none=True)
    @ns.response(201, 'timezone successfully created')
    @ns.response(400, 'Bad request')
    @ns.response(409, 'Conflict. Timezone with same name already exists')
    def post(self, username):
        """Creates a new timezone for a user"""
        utils.check_user_enabled()
        utils.validate_permissions(required_permission=UserRolesEnum.record_all.value, username=username)
        args = request.get_json(force=True)
        try:
            return qh.create_user_timezone(
                username,
                name=args['name'],
                timezone_id=args['timezone_id']
            )
        except KeyError:
            raise ValueError('missing required input parameter')


@ns.doc(security='apikey')
@ns.route('/<username>/<name>')
@ns.param('username', 'username')
@ns.param('name', 'timezone name')
@ns.response(404, 'Not found error')
class User(Resource):
    @ns.doc('get_user_timezone')
    @flask_jwt_extended.jwt_required
    @ns.marshal_with(serializers.Timezone)
    def get(self, username, name):
        """Get user timezone by id"""
        utils.check_user_enabled()
        utils.validate_permissions(required_permission=UserRolesEnum.record_all.value, username=username)
        return qh.get_user_timezone(username, name)

    @ns.doc('update_user_timezone')
    @flask_jwt_extended.jwt_required
    @ns.expect(serializers.Timezone, validate=True)
    @ns.response(200, 'User timezone successfully updated')
    @ns.response(400, 'Invalid user timezone data')
    def put(self, username, name):
        """Update user timezone"""
        utils.check_user_enabled()
        utils.validate_permissions(required_permission=UserRolesEnum.record_all.value, username=username)
        args = request.get_json(force=True)

        update = {}
        for key in ['name', 'timezone_id']:
            try:
                val = args[key]
                if not val:
                    raise ValueError('invalid input')
                update[key] = val
            except KeyError:
                pass

        if not update:
            return {}, 200

        qh.update_user_timezone(username, tz_name=name, **update)
        return {}, 200


    @ns.doc('delete_user_timezone')
    @flask_jwt_extended.jwt_required
    @ns.response(200, 'User timezone successfully removed')
    def delete(self, username, name):
        """Delete user timezone"""
        utils.check_user_enabled()
        utils.validate_permissions(required_permission=UserRolesEnum.record_all.value, username=username)
        qh.delete_user_timezone(username, name)
        return {}, 200
