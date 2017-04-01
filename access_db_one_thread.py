"""
Read/write to a simple test SQLite database via peewee and apsw
"""

from db_models import database, TestTable

database.connect()

select_q = TestTable.select()
print(f"Number of records in TestTable = {select_q.count()}")

for record in select_q:
    print(f'ID: {record.test_table}; text_value: {record.text_value} ' +
          f'last written date: {record.last_written_date}.')
