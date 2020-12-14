import mongoengine as me
from core.base import BaseModel


class User(BaseModel):
    email = me.StringField(max_length=128, required=True, unique=True)
    password = me.StringField(max_length=256, required=True)
    is_active = me.BooleanField(default=False)
