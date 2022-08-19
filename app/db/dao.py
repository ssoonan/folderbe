from typing import List
import pymysql


from ..model import Channel, Folder, User
from .helper import get_db


class Dao:
    def __init__(self, ):
        pass
    

class UserDao:
    def __init__(self) -> None:
        pass

    def find_by(value, key='id') -> User:
        sql = "select * from User where `{key}` = \"{}\"".format(value, key=key)
        cursor = get_db().cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        if result is None:
            return None
        return User(result['img'], result['name'], result['email'], result['refresh_token'], user_id=result['id'])

    def insert(user: User):
        sql = """insert into User (`name`, `img`, `email`, `refresh_token`) VALUES ("{}", "{}", "{}", "{}")""".format(user.name, user.user_img, user.email, user.refresh_token)
        cursor = get_db().cursor()
        cursor.execute(sql)
        get_db().commit()
        user.user_id = cursor.lastrowid
        cursor.close()

    def update(user: User):
        sql = "update User SET `img` = \"{}\", `refresh_token` = \"{}\" where `email` = \"{}\"".format(user.user_img, user.refresh_token, user.email)
        cursor = get_db().cursor()
        cursor.execute(sql)
        get_db().commit()
        cursor.close()

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

    def find_by_user(user: User) -> List[Folder]:
        sql = "select * from Folder where `user_id` = \"{}\"".format(user.user_id)
        cursor = get_db().cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        folders = []
        for result in results:
            folders.append(Folder(result['name'], result['user_id'], result['id']))
        return folders
    
    def insert(folder: Folder):
        sql = "insert into Folder (name, user_id) VALUES (%s, %s)"
        cursor = get_db().cursor()
        try:
            cursor.execute(sql, (folder.name, folder.user_id))
        except pymysql.err.IntegrityError:
            return False
        get_db().commit()
        folder.folder_id = cursor.lastrowid
        cursor.close()
        return True

    def update_channels(folder: Folder, channels: List[Channel]):
        pass