from datetime import datetime

from peewee import *

db = SqliteDatabase('db/ona_form.db')


class OnaForms(Model):
    form_id = IntegerField(unique=True, primary_key=True)
    form_name = CharField()
    form_title = CharField()
    description = CharField()
    url = CharField()
    created_at = DateTimeField(default=datetime.now())

    class Meta:
        database = db
        db_table = 'form_list'


def create_tables():
    db.connect()
    db.create_tables([OnaForms])
