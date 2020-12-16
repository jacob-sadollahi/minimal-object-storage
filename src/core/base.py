import mongoengine as me


class BaseModel(me.Document):
    meta = {
        'abstract': True
    }
    created = me.DateTimeField()
    modified = me.DateTimeField()
