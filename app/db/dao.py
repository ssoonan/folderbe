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
                result = cursor.execute(sql)
                get_db().commit()
                if not result:
                    return False
                return True
        except pymysql.err.Error as e:  #TODO: 에러 로그 기록
            print(e)
            return False
    
    def insert(self, sql, obj):
        try:
            with get_db().cursor() as cursor:
                cursor.execute(sql)
                get_db().commit()
                setattr(obj, "{}_id".format(obj), cursor.lastrowid)  # insert된 객체의 id 세팅
                return True
        except pymysql.err.IntegrityError:
            return False
    
    def insert_all(self, sql, param):
        try:
            with get_db().cursor() as cursor:
                cursor.executemany(sql, param)
                get_db().commit()
                return True
        except pymysql.err.Error as e:
            print(e)
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

    def update(user: User):  # TODO: 원하는 값만 넣어서 업데이트 할 수는 없나?
        sql = "update User SET `img` = \"{}\", `refresh_token` = \"{}\" where `email` = \"{}\"".format(user.user_img, user.refresh_token, user.email)
        dao.update(sql)

class ChannelDao:
    dao = dao

    def insert_whole_channels(channels: List[Channel], user: User):
        channels = [[channel.channel_id, channel.icon_img, channel.name] for channel in channels]
        channel_sql = "insert ignore into Channel (`id`, `icon_img`, `name`) Values (%s, %s, %s)"
        dao.insert_all(channel_sql, channels)
        channel_user_sql = "insert into User_Channel (`user_id`, `channel_id`) VALUES (%s, %s)"
        dao.insert_all(channel_user_sql, [[user.user_id, channel[0]] for channel in channels])

    def find_channels_from_user(user: User) -> List[Channel]:
        sql = """select c.id, c.playlist_id, c.name, c.icon_img from Channel c\
                inner join User_Channel u_c on u_c.channel_id = c.id\
                inner join User u on u.id = u_c.user_id where u.id = \"{}\"""".format(user.user_id)
        results = dao.query_all(sql)
        channels = []
        for result in results:
            channels.append(Channel(result['id'], result['icon_img'], result['name']))
        return channels
    
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
    
    def delete(folder_id):
        sql = "delete from Folder where id = \"{}\"".format(folder_id)
        return dao.update(sql)

    def update_channels(folder: Folder, channels: List[Channel]):
        pass