import mongoengine as me
from core.base import BaseModel
from apps.user.models import User


class Prefix(BaseModel):
    prefix = me.StringField(max_length=256, required=True)


class BucketPrefix(BaseModel):
    prefix = me.ReferenceField(Prefix, required=True)
    user = me.ReferenceField(User, required=True)
    is_allowed = me.BooleanField(required=True)
