"""
User Role API - for role management
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

ns = flask_api.namespace('user_role', validate=True, description=__doc__)

@ns.route('')
@ns.doc(security='apikey')
@ns.response(404, 'User role not found')
@ns.response(400, 'Bad request')
class ListUserRoles(Resource):
    @ns.doc('create_new_user_role')
    @flask_jwt_extended.jwt_required
    @ns.expect(serializers.UserRole, validate=True)
    @ns.marshal_with(serializers.UserRole, skip_none=True)
    @ns.response(200, 'User role successfully created')
    @ns.response(409, 'Conflict. User role already exists')
    def post(self):
        """Creates a new user role"""
        utils.check_user_enabled()
        utils.validate_permissions(required_permission=UserRolesEnum.role.value)
        args = request.get_json(force=True)
        try:
            return qh.create_user_role(role=args['role'], permissions=args['permissions'])
        except KeyError:
            raise ValueError('missing required input parameter')


    @ns.doc('list_all_user_roles')
    @flask_jwt_extended.jwt_required
    @ns.marshal_with(serializers.UserRolesList, skip_none=True)
    @ns.response(200, 'List of user roles retuned successfully')
    def get(self):
        """Get all user roles"""
        utils.check_user_enabled()
        utils.validate_permissions(required_permission=UserRolesEnum.role.value)
        roles = qh.get_user_roles()
        if not roles["data"]:
            return {}, 404
        return roles


@ns.route('/<role>')
@ns.doc(security='apikey')
@ns.param('role', 'User role')
@ns.response(404, 'User role not found')
class UserRole(Resource):
    @ns.doc('get_user_role')
    @flask_jwt_extended.jwt_required
    @ns.marshal_with(serializers.UserRole, skip_none=True)
    @ns.response(200, 'List of user roles retuned successfully')
    def get(self, role):
        """Get user role"""
        utils.check_user_enabled()
        utils.validate_permissions(required_permission=UserRolesEnum.role.value)
        user_role = qh.get_user_role(role)
        if not user_role:
            return {}, 404
        else:
            return user_role

    @ns.doc('delete_user_role')
    @flask_jwt_extended.jwt_required
    @ns.response(200, 'User role deleted successfully')
    def delete(self, role):
        """Delete a user role"""
        utils.check_user_enabled()
        utils.validate_permissions(required_permission=UserRolesEnum.role.value)
        qh.delete_user_role(role)
        return {}, 200
