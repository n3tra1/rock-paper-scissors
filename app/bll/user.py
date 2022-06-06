from fastapi_sqlalchemy import db
from app.db import models


def make_user():
    user = models.User()
    s = db.session
    s.add(user)
    s.commit()
    return user
