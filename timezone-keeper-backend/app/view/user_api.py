"""
User API - for user management
"""
import logging

from flask_restplus import Resource
from app.rest import flask_api
import app.view.serializers as serializers
import app.queries_handler as qh
from flask import request
import flask_jwt_extended
from app.storage.user_roles import UserRolesEnum
import app.view.utils as utils

log = logging.getLogger(__name__)

ns = flask_api.namespace('user', validate=True, description=__doc__)


@ns.route('')
class ListUsers(Resource):
    @ns.doc(security='apikey')
    @ns.doc('list_all_users')
    @flask_jwt_extended.jwt_required
    @ns.marshal_with(serializers.UserData, skip_none=True)
    @ns.response(200, 'User details retuned successfully')
    @ns.response(404, 'No Users found')
    @ns.response(400, 'Bad request')
    def get(self):
        """Get all users"""
        utils.check_user_enabled()
        username, perm = utils.get_user_permissions()
        users_data = qh.get_user_all(username, perm)
        if not users_data["data"]:
            return {}, 404
        return users_data

    @ns.doc('create_new_user')
    @ns.expect(serializers.UserWithPasswd, validate=True)
    @ns.marshal_with(serializers.User, skip_none=True)
    @ns.response(201, 'User successfully created')
    @ns.response(400, 'Bad request')
    @ns.response(409, 'Conflict. User already exists')
    def post(self):
        """Creates a new User"""
        args = request.get_json(force=True)
        try:
            return qh.create_user(
                first_name = args['first_name'],
                last_name = args['last_name'],
                username = args['username'],
                email = args['email'],
                password = args['password']
            )
        except KeyError:
            raise ValueError('missing required input parameter')

@ns.doc(security='apikey')
@ns.route('/<username>')
@ns.param('username', 'User name')
@ns.response(404, 'User not found')
class User(Resource):
    @ns.doc('get_user')
    @flask_jwt_extended.jwt_required
    @ns.marshal_with(serializers.User)
    @ns.response(200, 'User successfully returned')
    def get(self, username):
        """Get user by username"""
        utils.check_user_enabled()
        req_user, perm = utils.get_user_permissions()
        user = qh.get_user(username, req_user, perm)
        if not user:
            ns.abort(404)
        else:
            return user

    @ns.doc('update_user')
    @flask_jwt_extended.jwt_required
    @ns.expect(serializers.UserUpdatable, validate=True)
    @ns.response(200, 'User successfully updated')
    @ns.response(400, 'Invalid user data')
    def put(self, username):
        """Update user"""
        utils.check_user_enabled()
        args = request.get_json(force=True)

        update = {}
        for key in ['first_name', 'last_name', 'email', 'password', 'role']:
            try:
                val = args[key]
                if not val:
                    raise ValueError('invalid input')
                update[key] = val
            except KeyError:
                pass

        if not update:
            return {}, 200
        req_user, perm = utils.get_user_permissions()
        qh.update_user(username, req_user, perm, **update)
        return {}, 200


    @ns.doc('delete_user')
    @flask_jwt_extended.jwt_required
    @ns.response(200, 'User successfully removed')
    @ns.response(400, 'Bad request')
    def delete(self, username):
        """Delete user"""
        utils.check_user_enabled()
        req_user, perm = utils.get_user_permissions()
        qh.delete_user(username, req_user, perm)
        return {}, 200

@ns.doc(security='apikey')
@ns.route('/<username>/enable')
@ns.param('username', 'User name')
@ns.response(404, 'User not found')
@ns.response(200, 'User account enabled')
class UserEnable(Resource):
    @ns.doc('enable_user')
    @flask_jwt_extended.jwt_required
    def post(self, username):
        """enable user account"""
        utils.check_user_enabled()
        utils.validate_permissions(required_permission=UserRolesEnum.user_all.value)
        qh.enable_user(username, True)
        return {}, 200

@ns.doc(security='apikey')
@ns.route('/<username>/disable')
@ns.param('username', 'User name')
@ns.response(404, 'User not found')
@ns.response(200, 'User account disabled')
class UserEnable(Resource):
    @ns.doc('disable_user')
    @flask_jwt_extended.jwt_required
    def post(self, username):
        """disable user account"""
        utils.check_user_enabled()
        utils.validate_permissions(required_permission=UserRolesEnum.user_all.value)
        qh.enable_user(username, False)
        return {}, 200