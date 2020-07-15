import logging
import sqlalchemy
import passlib.hash
from app.storage.db import db

log = logging.getLogger(__name__)

class UserDetails(db.Model):
    """contains user specific information"""
    __tablename__ = 'UserDetails'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    role_id = db.Column(db.String, db.ForeignKey('UserRoles.id'))
    enabled = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return (f'<id={self.id}, first_name={self.first_name}, last_name={self.last_name}, username={self.username}, '
                f'email={self.email}, passwd={self.password}, role_id={self.role_id}, enabled={self.enabled}>')


    def to_dict(self):
        """
        return dictionary representation
        """
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'role_id': self.role_id,
            'enabled': self.enabled
        }


    @classmethod
    def get(cls, username):
        """
        get a user's details
        """
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def get_all(cls):
        """
        get all users
        """
        result = cls.query.all()
        return list(result)

    @classmethod
    def delete(cls, username):
        """
        delete user matching username
        """
        try:
            user = cls.query.filter_by(username=username).one()
            db.session.delete(user)
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def delete_all(cls):
        """
        delete all users
        """
        try:
            nr_deleted = db.session.query(cls).delete()
            db.session.commit()
            return nr_deleted
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def generate_hash(password):
        if not password:
            return None
        return passlib.hash.bcrypt.hash(password)

    @staticmethod
    def verify_hash(supplied_password, stored_password):
        if not supplied_password:
            return False
        if not stored_password:
            return False
        return passlib.hash.bcrypt.verify(supplied_password, stored_password)


@sqlalchemy.event.listens_for(UserDetails.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
    from app.storage.user_roles import UserRoles
    admin_user = UserRoles.get('admin')
    if not admin_user:
        raise ValueError('User Details table dependency missing')

    log.info('populating user details table')
    try:
        db.session.add(
            UserDetails(
                first_name='Administrator',
                last_name='SuperUser',
                username='admin',
                email='admin@timezonekeeper.com',
                password=UserDetails.generate_hash('admin'),
                role_id=admin_user['id'],
                enabled=True
            )
        )
        db.session.commit()
    except Exception as ex:
        log.error('failed to initialize user details db: {ex}')
        raise ValueError('Database initialization failed!')