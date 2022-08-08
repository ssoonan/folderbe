from flask import g, current_app
import pymysql
import click

def parse_sql(filename):
    data = open(filename, 'r').readlines()
    stmts = []
    DELIMITER = ';'
    stmt = ''

    for lineno, line in enumerate(data):
        if not line.strip():
            continue

        if line.startswith('--'):
            continue

        if 'DELIMITER' in line:
            DELIMITER = line.split()[1]
            continue

        if (DELIMITER not in line):
            stmt += line.replace(DELIMITER, ';')
            continue

        if stmt:
            stmt += line
            stmts.append(stmt.strip())
            stmt = ''
        else:
            stmts.append(line.strip())
    return stmts


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = pymysql.connect(host="localhost",
                                           user="root",
                                           password="test",
                                           database="folderbe")
    return db

def init_db():
    db = get_db()
    stmts = parse_sql('schema.sql')
    with db.cursor() as cursor:
        for stmt in stmts:
            cursor.execute(stmt)
        db.commit()



@current_app.teardown_appcontext
def close_db():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


class UserDao:
    def __init__(self) -> None:
        pass

    def findByUserId(user_id):
        sql = "select * from User where id = {}".format(user_id)
        g.db.cursor().  