from turtle import update
from typing import List
from functools import wraps
import pymysql


from ..model import Channel, Folder, User
from .helper import get_db


class Dao:
    def update(self, sql):
        try:
            with get_db().cursor() as cursor:
                cursor.execute(sql)
                get_db().commit()
                return True
        except pymysql.err.Error:
            return False
    
    def insert(self, sql, obj):
        try:
            with get_db().cursor() as cursor:
                cursor.execute(sql)
                get_db().commit()
                setattr(obj, "{}_id".format(obj), cursor.lastrowid)
                return True
        except pymysql.err.IntegrityError:
            return False

    def query_one(self, sql):
        with get_db().cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchone()

    def query_all(self, sql):
        with get_db().cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


dao = Dao()


class UserDao:
    dao = dao

    def find_by(value, key='id') -> User:
        sql = "select * from User where `{key}` = \"{}\"".format(value, key=key)
        result = dao.query_one(sql)
        if result is None:
            return None
        return User(result['img'], result['name'], result['email'], result['refresh_token'], user_id=result['id'])

    def insert(user: User):
        sql = """insert into User (`name`, `img`, `email`, `refresh_token`) VALUES ("{}", "{}", "{}", "{}")""".format(user.name, user.user_img, user.email, user.refresh_token)
        dao.insert(sql, user)

    def update(user: User):
        sql = "update User SET `img` = \"{}\", `refresh_token` = \"{}\" where `email` = \"{}\"".format(user.user_img, user.refresh_token, user.email)
        dao.update(sql)

class ChannelDao:
    dao = dao

    def find_channels_from_user(user: User) -> List[Channel]:
        pass
    
    def find_channels_from_folder(folder: Folder) -> List[Channel]:
        pass


class FolderDao:
    dao = dao

    def find_by_user(user: User) -> List[Folder]:
        sql = "select * from Folder where `user_id` = \"{}\"".format(user.user_id)
        results = dao.query_all(sql)
        folders = []
        for result in results:  # TODO: 이 세팅도 한 번에 넘길 수 있게
            folders.append(Folder(result['name'], result['user_id'], result['id']))
        return folders
    
    def insert(folder: Folder):
        sql = "insert into Folder (name, user_id) VALUES (\"{}\", \"{}\")".format(folder.name, folder.user_id)
        return dao.insert(sql, folder)
    
    def delete(folder: Folder):
        sql = "delete from Folder where id = \"{}\"".format(folder.folder_id)
        return dao.update(sql)

    def update_channels(folder: Folder, channels: List[Channel]):
        pass