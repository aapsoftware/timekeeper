import flask
import flask_jwt_extended
import json
import app.error as error
from test.base import BaseTestCase
from test import test_helpers as th
from app.storage.user_details import UserDetails
from app.storage.user_roles import UserRoles
from app.storage.db import db


class TestUserApi(BaseTestCase):
    """User test stubs"""

    def setUp(self):
        '''called before each test'''
        # admin is already in the db
        user = UserRoles.get('user')
        manager_user = UserRoles.get('manager')

        db.session.add(
            UserDetails(
                first_name='user_first_name',
                last_name='user_last_name',
                username='user',
                email='user@timezonekeeper.com',
                password=UserDetails.generate_hash('user'),
                role_id=user['id'],
                enabled=True
            )
        )

        db.session.add(
            UserDetails(
                first_name='manager_first_name',
                last_name='manager_last_name',
                username='manager',
                email='manager@timezonekeeper.com',
                password=UserDetails.generate_hash('manager'),
                role_id=manager_user['id'],
                enabled=True
            )
        )
        db.session.commit()

    def tearDown(self):
        '''called after each test'''
        db.session.remove()
        db.drop_all()

    def test_get_all_users_admin(self):
        admin_user = th.get_user_details('admin')
        access_token = flask_jwt_extended.create_access_token(identity=admin_user)

        response = self.client.open(
            '/api/v1/user',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 200)

        data = response.json['data']

        self.assertEqual(len(UserDetails.get_all()), 3)
        self.assertEqual(len(data), 3)

        self.assertEqual(data[0]['first_name'], 'Administrator')
        self.assertEqual(data[0]['last_name'], 'SuperUser')
        self.assertEqual(data[0]['username'], 'admin')
        self.assertEqual(data[0]['email'], 'admin@timezonekeeper.com')
        self.assertEqual(data[0]['role'], 'admin')
        self.assertEqual(data[0]['enabled'], True)
        self.assertNotIn('password', data[0])

        self.assertEqual(data[1]['first_name'], 'user_first_name')
        self.assertEqual(data[1]['last_name'], 'user_last_name')
        self.assertEqual(data[1]['username'], 'user')
        self.assertEqual(data[1]['email'], 'user@timezonekeeper.com')
        self.assertEqual(data[1]['role'], 'user')
        self.assertEqual(data[1]['enabled'], True)
        self.assertNotIn('password', data[1])

        self.assertEqual(data[2]['first_name'], 'manager_first_name')
        self.assertEqual(data[2]['last_name'], 'manager_last_name')
        self.assertEqual(data[2]['username'], 'manager')
        self.assertEqual(data[2]['email'], 'manager@timezonekeeper.com')
        self.assertEqual(data[2]['role'], 'manager')
        self.assertEqual(data[2]['enabled'], True)
        self.assertNotIn('password', data[2])

    def test_get_all_users_manager(self):
        user = th.get_user_details('manager')
        access_token = flask_jwt_extended.create_access_token(identity=user)

        response = self.client.open(
            '/api/v1/user',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 200)

        data = response.json['data']

        self.assertEqual(len(UserDetails.get_all()), 3)
        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]['first_name'], 'user_first_name')
        self.assertEqual(data[0]['last_name'], 'user_last_name')
        self.assertEqual(data[0]['username'], 'user')
        self.assertEqual(data[0]['email'], 'user@timezonekeeper.com')
        self.assertEqual(data[0]['role'], 'user')
        self.assertEqual(data[0]['enabled'], True)
        self.assertNotIn('password', data[0])


    def test_get_all_users_user(self):
        user = th.get_user_details('user')
        access_token = flask_jwt_extended.create_access_token(identity=user)

        response = self.client.open(
            '/api/v1/user',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 200)

        data = response.json['data']

        self.assertEqual(len(UserDetails.get_all()), 3)
        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]['first_name'], 'user_first_name')
        self.assertEqual(data[0]['last_name'], 'user_last_name')
        self.assertEqual(data[0]['username'], 'user')
        self.assertEqual(data[0]['email'], 'user@timezonekeeper.com')
        self.assertEqual(data[0]['role'], 'user')
        self.assertEqual(data[0]['enabled'], True)
        self.assertNotIn('password', data[0])

    def test_get_all_users_missing_auth_header(self):
        response = self.client.open(
            '/api/v1/user',
            method='GET',
            content_type='application/json'
        )
        self.assertStatus(response, 401)

    def test_get_all_users_invalid_token(self):
        response = self.client.open(
            '/api/v1/user',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer testing'}
        )
        self.assertStatus(response, 401)

    def test_get_user_admin(self):
        admin_user = th.get_user_details('admin')
        access_token = flask_jwt_extended.create_access_token(identity=admin_user)

        username = 'admin'
        response = self.client.open(
            f'/api/v1/user/{username}',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 200)

        data = response.json

        self.assertEqual(data['first_name'], 'Administrator')
        self.assertEqual(data['last_name'], 'SuperUser')
        self.assertEqual(data['username'], 'admin')
        self.assertEqual(data['email'], 'admin@timezonekeeper.com')
        self.assertEqual(data['role'], 'admin')
        self.assertEqual(data['enabled'], True)
        self.assertNotIn('password', data)

        username = 'user'
        response = self.client.open(
            f'/api/v1/user/{username}',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 200)

        data = response.json

        self.assertEqual(data['first_name'], 'user_first_name')
        self.assertEqual(data['last_name'], 'user_last_name')
        self.assertEqual(data['username'], 'user')
        self.assertEqual(data['email'], 'user@timezonekeeper.com')
        self.assertEqual(data['role'], 'user')
        self.assertEqual(data['enabled'], True)
        self.assertNotIn('password', data)

        username = 'manager'
        response = self.client.open(
            f'/api/v1/user/{username}',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 200)

        data = response.json

        self.assertEqual(data['first_name'], 'manager_first_name')
        self.assertEqual(data['last_name'], 'manager_last_name')
        self.assertEqual(data['username'], 'manager')
        self.assertEqual(data['email'], 'manager@timezonekeeper.com')
        self.assertEqual(data['role'], 'manager')
        self.assertEqual(data['enabled'], True)
        self.assertNotIn('password', data)


    def test_get_user_manager(self):
        user = th.get_user_details('manager')
        access_token = flask_jwt_extended.create_access_token(identity=user)

        username = 'admin'
        response = self.client.open(
            f'/api/v1/user/{username}',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 403)

        username = 'user'
        response = self.client.open(
            f'/api/v1/user/{username}',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 200)

        data = response.json

        self.assertEqual(data['first_name'], 'user_first_name')
        self.assertEqual(data['last_name'], 'user_last_name')
        self.assertEqual(data['username'], 'user')
        self.assertEqual(data['email'], 'user@timezonekeeper.com')
        self.assertEqual(data['role'], 'user')
        self.assertEqual(data['enabled'], True)
        self.assertNotIn('password', data)

        username = 'manager'
        response = self.client.open(
            f'/api/v1/user/{username}',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 200)

        data = response.json

        self.assertEqual(data['first_name'], 'manager_first_name')
        self.assertEqual(data['last_name'], 'manager_last_name')
        self.assertEqual(data['username'], 'manager')
        self.assertEqual(data['email'], 'manager@timezonekeeper.com')
        self.assertEqual(data['role'], 'manager')
        self.assertEqual(data['enabled'], True)
        self.assertNotIn('password', data)


    def test_get_user_user_role(self):
        user = th.get_user_details('user')
        access_token = flask_jwt_extended.create_access_token(identity=user)

        username = 'admin'
        response = self.client.open(
            f'/api/v1/user/{username}',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 403)

        username = 'user'
        response = self.client.open(
            f'/api/v1/user/{username}',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 200)

        data = response.json

        self.assertEqual(data['first_name'], 'user_first_name')
        self.assertEqual(data['last_name'], 'user_last_name')
        self.assertEqual(data['username'], 'user')
        self.assertEqual(data['email'], 'user@timezonekeeper.com')
        self.assertEqual(data['role'], 'user')
        self.assertEqual(data['enabled'], True)
        self.assertNotIn('password', data)

        username = 'manager'
        response = self.client.open(
            f'/api/v1/user/{username}',
            method='GET',
            content_type='application/json',
            headers = {'Authorization': 'Bearer ' + access_token}
        )
        self.assertStatus(response, 403)
