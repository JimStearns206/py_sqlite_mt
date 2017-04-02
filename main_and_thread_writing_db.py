"""
Read/write to a simple test SQLite database via peewee and apsw
on both the main thread and a special-purpose thread
"""
import threading
import time
from typing import Type

from apsw import BusyError

from db_models import database, TestTable


class Signal:
    go = True


def write_records(peewee_table: Type[TestTable], n_recs_max, first_rec_num=0,
                  signal=None, sleep=0.01):
    n_recs_written = 0
    n_exceptions = 0
    while n_recs_written < n_recs_max:
        if signal and not signal.go:
            print(f"Received stop signal.")
            break
        try:
            record = peewee_table(text_value=str(first_rec_num + n_recs_written))
            record.save()
            n_recs_written += 1
        except BusyError:
            print(f"BusyError exception writing {n_recs_written}; retrying.")
            n_exceptions += 1

        # Allow context switch so that row inserts of multiple threads
        # can be interleaved.
        sleep = sleep if sleep else 0
        time.sleep(sleep)

    if n_recs_written == n_recs_max:
        print(f"Wrote the requested {n_recs_written} starting at {first_rec_num}.")
    else:
        print(f"Wrote {n_recs_written} records.")
    print(f"Number of exceptions: {n_exceptions}.")


def read_table():
    select_q = TestTable.select()
    print(f"Number of records in TestTable = {select_q.count()}")
    for record in select_q:
        print(f'ID: {record.test_table}; text_value: {record.text_value} ' +
              f'last written date: {record.last_written_date}.')


def empty_test_table(tt: Type[TestTable]):
    """ This operation can exceed a timeout of 1 second with '000s of records
    delete_q = tt.delete()
    start_time = time.time()
    try:
        n_rows_deleted = delete_q.execute()
        elapsed_time = time.time() - start_time
        print(f"Deleted {n_rows_deleted} rows in TestTable in {elapsed_time:.2f} seconds.")
    except BusyError as be:
        elapsed_time = time.time() - start_time
        print(f"BusyError exception. Operation failed after {elapsed_time:0.2f} seconds.")
    """
    # Avoid timeout by deleting each record separately.
    # More elapsed time, but in smaller chunks of DB operations
    start_time = time.time()
    try:
        select_q = tt.select()
        print(f"{select_q.count()} rows selected for deletion.")
        n_rows_deleted = 0
        for row in select_q:
            row.delete_instance()
            n_rows_deleted += 1

        elapsed_time = time.time() - start_time
        print(f"Deleted {n_rows_deleted} rows in TestTable in " +
              f"{elapsed_time:.2f} seconds.")
    except BusyError:
        elapsed_time = time.time() - start_time
        print(f"BusyError exception. Operation failed after " +
              f"{elapsed_time:0.2f} seconds deleting {n_rows_deleted} rows.")


def setup():
    # local_database_variable = database
    print(f"APSW Driver Timeout = {database.timeout} ms")
    empty_test_table(TestTable)


def supervisor():
    start_time = time.time()
    thread1_signal = Signal()
    db_writer_thread1 = threading.Thread(target=write_records,
                                         args=(TestTable,
                                               1000),
                                         kwargs={
                                            'first_rec_num': 10000,
                                            'signal': thread1_signal,
                                            'sleep': 0.01}
                                         )
    db_writer_thread1.start()

    thread2_signal = Signal()
    db_writer_thread2 = threading.Thread(target=write_records,
                                         args=(TestTable,
                                               1000),
                                         kwargs={
                                            'first_rec_num': 20000,
                                            'signal': thread2_signal,
                                            'sleep': 0.01}
                                         )
    db_writer_thread2.start()

    print("Supervisor: threads started.")
    write_records(TestTable, 1000, first_rec_num=0)
    db_writer_thread1.join()
    db_writer_thread2.join()
    elapsed_time = time.time() - start_time
    print(f"Supervisor: threads completed in {elapsed_time:.1f} seconds.")


def main():
    setup()
    supervisor()

if __name__ == '__main__':
    main()
