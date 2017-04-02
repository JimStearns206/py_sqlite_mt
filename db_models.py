from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.apsw_ext import APSWDatabase


# Standard SQLite: database = SqliteDatabase('data/test.sqlite3')

# Playhouse extensions: database = SqliteExtDatabase('data/test.sqlite3',
#       journal_mode='WAL')

# APSW SQLite Driver, which is faster and provides:
# "Connections can be shared across threads without any additional locking"
database = APSWDatabase('data/test.sqlite3', timeout=1000)

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class TestTable(BaseModel):
    last_written_date = TextField(db_column='LAST_WRITTEN_DATE', null=True)
    test_table = PrimaryKeyField(db_column='TEST_TABLE_ID')
    text_value = TextField(db_column='TEXT_VALUE', null=True)

    class Meta:
        db_table = 'TEST_TABLE'
