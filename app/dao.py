from flask import g, current_app
from typing import List
import pymysql
import click

from app.model import Channel, Folder, User

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


class Dao:
    def __init__(self, ):
        pass
    


class UserDao:
    def __init__(self) -> None:
        pass

    def find_by_id(user_id) -> User:
        sql = "select * from User where id = {}".format(user_id)
    
    def insert(user: User):
        pass


class ChannelDao:
    def __init__(self) -> None:
        pass

    def find_channels_from_user(user: User) -> List[Channel]:
        pass
    
    def find_channels_from_folder(folder: Folder) -> List[Channel]:
        pass


class FolderDao:
    def __init__(self) -> None:
        pass

    def find_by_user(user: User) -> Folder:
        pass
    
    def insert(folder: Folder):
        pass

    def update_channels(folder: Folder, channels: List[Channel]):
        pass