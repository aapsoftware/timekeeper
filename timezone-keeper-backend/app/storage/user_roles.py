import logging
import sqlalchemy
import enum

from app.storage.db import db

log = logging.getLogger(__name__)

class UserRolesEnum(enum.Enum):
    """allowed user roles permissions"""
    record = 'CRUD-own-records'
    record_all = 'CRUD-all-records'
    user = 'CRUD-own-user-details'
    user_privileged = 'CRUD-non-privileged-user-details'
    user_all = 'CRUD-all-user-details'
    role = 'CRUD-user-roles'

    @classmethod
    def values(cls):
        """
        return a list of all values in enum
        :return:
        """
        return [item.value for item in cls]


class UserRoles(db.Model):
    """contains user roles information"""
    __tablename__ = 'UserRoles'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String, unique=True, nullable=False)
    permissions = db.Column(db.String, nullable=False)

    def __repr__(self):
        return (f'<id={self.id}, role={self.role}, permissions={self.permissions}>')


    def to_dict(self):
        """
        return dictionary representation
        """
        return {
            'id': self.id,
            'role': self.role,
            'permissions':self.permissions.split(',')
        }

    @classmethod
    def get(cls, role):
        """
        get a user role
        """
        record = cls.query.filter_by(role=role).one_or_none()
        record = record.to_dict() if record else None
        return record

    @classmethod
    def get_all(cls):
        """
        get all user roles
        """
        result = cls.query.all()
        return [x.to_dict() for x in result]

    @classmethod
    def delete(cls, user_role):
        """
        delete user role
        """
        try:
            role = cls.query.filter_by(role=user_role).one()
            db.session.delete(role)
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

@sqlalchemy.event.listens_for(UserRoles.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
    log.info('populating user roles table')
    try:
        permissions = [
            UserRolesEnum.record.value,
            UserRolesEnum.user.value
        ]
        db.session.add(
            UserRoles(
                role='user',
                permissions=",".join(permissions)
            )
        )
        permissions = [
            UserRolesEnum.record.value,
            UserRolesEnum.user_privileged.value
        ]
        db.session.add(
            UserRoles(
                role='manager',
                permissions=",".join(permissions)
            )
        )
        permissions = [
            UserRolesEnum.role.value,
            UserRolesEnum.record_all.value,
            UserRolesEnum.user_all.value
        ]
        db.session.add(
            UserRoles(
                role='admin',
                permissions=",".join(permissions)
            )
        )
        db.session.commit()
    except Exception as ex:
        log.error('failed to initialize user roles db: {ex}')
        raise ValueError('Database initialization failed!')
