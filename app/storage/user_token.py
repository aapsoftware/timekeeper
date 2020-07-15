import logging
import sqlalchemy
import datetime
import jwt

from app.storage.db import db

log = logging.getLogger(__name__)

class RevokedUserTokens(db.Model):
    """contains revoked user tokens"""
    __tablename__ = 'RevokedUserTokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), index=True, unique=True, nullable=False)
    revoke_ts = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return (f'<id={self.id}, jti={self.jti}, revoke_ts={self.revoke_ts}>')


    def to_dict(self):
        """
        return dictionary representation
        """
        return {
            'id': self.id,
            'jti': self.jti,
            'revoke_ts': self.revoke_ts
        }

    @classmethod
    def get_all(cls):
        """
        get all revoked tokens
        """
        result = cls.query.all()
        return list(result)

    @classmethod
    def delete_all(cls):
        """
        delete all revoked tokens
        """
        try:
            nr_deleted = db.session.query(cls).delete()
            db.session.commit()
            return nr_deleted
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def is_blacklisted(cls, jti):
        '''
        checks if token jti is revoked
        '''
        token_jti = cls.query.filter_by(jti=jti).one_or_none()
        return token_jti is not None