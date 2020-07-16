import logging
import sqlalchemy

from app.storage.db import db

log = logging.getLogger(__name__)

class UserTimeZones(db.Model):
    """contains user timezones"""
    __tablename__ = 'UserTimezones'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('UserDetails.id'))
    timezone_id = db.Column(db.Integer(), db.ForeignKey('TimeZones.id'))
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return (f'<id={self.id}, user_id={self.user_id}, name={self.name}, timezone_id={self.timezone_id}>')


    def to_dict(self):
        """
        return dictionary representation
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timezone_id': self.timezone_id,
            'name': self.name
        }

    @classmethod
    def get(cls, id_):
        """
        get a user timezone
        """
        return cls.query.filter_by(id=id_).one_or_none()

    @classmethod
    def get_all(cls):
        """
        get all user timesones
        """
        result = cls.query.all()
        return list(result)

    @classmethod
    def delete(cls, id_):
        """
        delete user timezone matching id
        """
        try:
            role = cls.query.filter_by(id=id_).one()
            db.session.delete(role)
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def delete_all(cls):
        """
        delete all timezones
        """
        try:
            nr_deleted = db.session.query(cls).delete()
            db.session.commit()
            return nr_deleted
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            raise
