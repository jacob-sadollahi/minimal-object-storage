import mongoengine as me
from mongoengine import DoesNotExist, QuerySet


class BaseModel(me.Document):
    meta = {
        'abstract': True
    }
    created = me.DateTimeField()
    modified = me.DateTimeField()
