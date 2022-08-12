from sqlite3 import Cursor
from typing import List


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
        return User(result['img'], result['name'], result['email'], user_id=result['id'])

    def insert(user: User):
        sql = """insert into User (`name`, `img`, `email`, `refresh_token`) VALUES ("{}", "{}", "{}", "{}")""".format(user.name, user.user_img, user.email, user.refresh_token)
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

    def find_by_user(user: User) -> Folder:
        pass
    
    def insert(folder: Folder):
        pass

    def update_channels(folder: Folder, channels: List[Channel]):
        pass