from flask import g, Flask
import pymysql
import click


def parse_sql(filename):
    data = open(filename, 'r').readlines()
    stmts = []
    DELIMITER = ';'
    stmt = ''

    for _, line in enumerate(data):
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


def get_db() -> pymysql.connect:
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = pymysql.connect(host="localhost",
                                           user="root",
                                           password="test",
                                           database='folderbe')
    return db


def init_db():
    db = pymysql.connect(host="localhost",
                         user="root",
                         password="test")
    stmts = parse_sql('app/db/schema.sql')
    with db.cursor() as cursor:
        for stmt in stmts:
            cursor.execute(stmt)
        db.commit()


def close_db(e=None):
    db = g.pop('_database', None)
    if db is not None:
        db.close()


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo("database is initialized")


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)