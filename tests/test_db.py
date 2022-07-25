import pytest
import random

from .test_db_manager import db_connect


@pytest.fixture
def db():
    return db_connect()


def test_create_table(db):
    sql = '''
        CREATE TABLE IF NOT EXISTS test(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name VARCHAR NOT NULL
        );
    '''

    cur = db.cursor()
    cur.execute(sql)
    db.commit()

    sql = '''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='test';
    '''
    cur.execute(sql)
    row = cur.fetchall()

    db.close()

    assert len(row) == 1


def test_insert_into_table(db):
    cur = db.cursor()

    for i in range(0, 5):
        sql = '''
            INSERT INTO test(user_id, name)
            VALUES(?, ?);
        '''

        cur.execute(sql, (random.randrange(100000, 999999), f"Tester_{i}"))

    db.commit()

    sql = '''
        SELECT * FROM test;
    '''

    cur.execute(sql)
    rows = cur.fetchall()

    db.close()

    assert len(rows) == 5


def test_drop_table(db):
    sql = '''
        DROP TABLE test;
    '''

    cur = db.cursor()
    cur.execute(sql)
    db.commit()

    sql = '''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='test';
        '''
    cur.execute(sql)
    row = cur.fetchall()

    db.close()

    assert len(row) == 0
