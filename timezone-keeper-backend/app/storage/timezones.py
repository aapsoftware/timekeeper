import logging
import sqlalchemy
import flask
import json

from app.storage.db import db

log = logging.getLogger(__name__)

class TimeZones(db.Model):
    """contains predefined timezones"""
    __tablename__ = 'TimeZones'

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    relative_to_gmt = db.Column(db.String, nullable=False)

    def __repr__(self):
        return (f'<id={self.id}, location={self.location}, city={self.city}, relative_to_gmt={self.relative_to_gmt}>')

    def to_dict(self):
        """
        return dictionary representation
        """
        return {
            'id': self.id,
            'location': self.location,
            'city': self.city,
            'relative_to_gmt': self.relative_to_gmt
        }

    @classmethod
    def get(cls, id_):
        """
        get a timezone
        """
        return cls.query.filter_by(id=id_).one_or_none()

    @classmethod
    def get_all(cls):
        """
        get all timesones
        """
        result = cls.query.all()
        return list(result)

    @classmethod
    def delete(cls, id_):
        """
        delete user matching id
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


@sqlalchemy.event.listens_for(TimeZones.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
    log.info('populating timezones table')
    try:
        with open(flask.current_app.config['TIMEZONE_INITIAL_VALUES']) as json_file:
            data = json.load(json_file)
        for key, value in data.items():
            #we're only interested in the value which include a city name
            if '/' in key:
                location = key.split('/')
                db.session.add(
                    TimeZones(
                        location='/'.join(location[:-1]),
                        city=location[-1],
                        relative_to_gmt=value
                    )
                )

        db.session.commit()
    except Exception as ex:
        log.error('failed to initialize timezones db: {ex}')
        raise ValueError('Database initialization failed!')