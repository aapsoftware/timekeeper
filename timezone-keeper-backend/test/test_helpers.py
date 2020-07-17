
from app.storage.db import db
from app.storage.user_details import UserDetails
from app.storage.user_roles import UserRoles

def get_user_details(username):
    query = db.session.query(UserDetails, UserRoles).outerjoin(UserRoles, UserRoles.id == UserDetails.role_id)
    res = query.filter(UserDetails.username == username).one()

    user = res.UserRoles.to_dict()
    user.update(res.UserDetails.to_dict())
    return user