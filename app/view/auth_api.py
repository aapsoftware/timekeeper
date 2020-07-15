"""
Auth API - manages user authentication
"""
import logging
from flask_restplus import Resource
from app.rest import flask_api
import app.view.serializers as serializers
import app.queries_handler as qh
from flask import request
import flask_jwt_extended

log = logging.getLogger(__name__)

ns = flask_api.namespace('auth', validate=True, description=__doc__)

@ns.route('/login')
@ns.response(200, 'Success')
@ns.response(401, 'Unauthenticated')
class UserLogin(Resource):
    @ns.doc('login')
    @ns.expect(serializers.UserAuth, validate=True)
    def post(self):
        """
        Returns JWT token on successful login
        """
        args = request.get_json(force=True)
        try:
            return qh.authenticate_user(
                username = args['username'],
                passwd = args['password']
            )
        except KeyError:
            raise ValueError('missing required input parameter')


@ns.route('/logout')
@ns.doc(security='apikey')
@ns.response(200, 'Success')
class UserLogin(Resource):
    @ns.doc('logout')
    @flask_jwt_extended.jwt_required
    def post(self):
        """
        Revoke the current user's access token
        """
        jti = flask_jwt_extended.get_raw_jwt()['jti']
        qh.revoke_token(jti)
        log.info(f'successfully logged out user {flask_jwt_extended.get_jwt_identity()}')
        return {}, 200