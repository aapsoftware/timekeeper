import flask
import flask_jwt_extended
import json
import app.error as error
from test.base import BaseTestCase
from app.storage.user_token import RevokedUserTokens
from app.storage.db import db


class TestAuthApi(BaseTestCase):
    """Auth test stubs"""

    def tearDown(self):
        '''called after each test method'''
        db.session.remove()
        db.drop_all()

    def test_get_token(self):
        username = 'admin'
        passw = 'admin'

        response = self.client.open(
            '/api/v1/auth/login',
            method='POST',
            content_type='application/json',
            data=json.dumps({"username": username, "password": passw})
        )

        self.assertStatus(response, 200)
        self.assertIn('access_token', response.json)

    def test_get_token_missin_passwd(self):
        username = 'admin'
        passw = 'admin'

        response = self.client.open(
            '/api/v1/auth/login',
            method='POST',
            content_type='application/json',
            data=json.dumps({"username": username})
        )

        self.assertStatus(response, 400)

    def test_get_token_missin_user(self):
        username = 'admin'
        passw = 'admin'

        response = self.client.open(
            '/api/v1/auth/login',
            method='POST',
            content_type='application/json',
            data=json.dumps({"password": passw})
        )

        self.assertStatus(response, 400)

    def test_get_token_invalid_creds(self):
        response = self.client.open(
            '/api/v1/auth/login',
            method='POST',
            content_type='application/json',
            data=json.dumps({"username": 'test', "password": 'test'})
        )

        self.assertStatus(response, 401)

    def test_logout(self):
        user = {
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test',
            'role': 'admin',
            'permissions': 'CRUD-user-roles',
            'enabled': True
        }
        access_token = flask_jwt_extended.create_access_token(identity=user)

        revoked_tokens = RevokedUserTokens.get_all()
        self.assertEqual(len(revoked_tokens), 0)

        response = self.client.open(
            '/api/v1/auth/logout',
            method='POST',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 200)

        revoked_tokens = RevokedUserTokens.get_all()
        self.assertEqual(len(revoked_tokens), 1)

    def test_logout_missing_auth_heder(self):
        response = self.client.open(
            '/api/v1/auth/logout',
            method='POST',
            content_type='application/json'
        )
        self.assertStatus(response, 401)

    def test_logout_invalid_token(self):
        response = self.client.open(
            '/api/v1/auth/logout',
            method='POST',
            content_type='application/json',
            headers = {'Authorization': 'Bearer this_wont_work'}
        )
        self.assertStatus(response, 401)

    def test_logout_reuse_revoked_token(self):
        user = {
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test',
            'role': 'admin',
            'permissions': 'CRUD-user-roles',
            'enabled': True
        }
        access_token = flask_jwt_extended.create_access_token(identity=user)

        revoked_tokens = RevokedUserTokens.get_all()
        self.assertEqual(len(revoked_tokens), 0)

        response = self.client.open(
            '/api/v1/auth/logout',
            method='POST',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 200)

        response = self.client.open(
            '/api/v1/auth/logout',
            method='POST',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 401)

    def test_get_all_users_inactive_account(self):
        from app.storage.user_details import UserDetails
        db.session.add(
            UserDetails(
                first_name='test',
                last_name='test',
                username='test',
                email='testr@timezonekeeper.com',
                password=UserDetails.generate_hash('test'),
                role_id=1,
                enabled=False
            )
        )
        db.session.commit()

        username = 'test'
        passw = 'test'

        response = self.client.open(
            '/api/v1/auth/login',
            method='POST',
            content_type='application/json',
            data=json.dumps({"username": username, "password": passw})
        )

        self.assertStatus(response, 401)
