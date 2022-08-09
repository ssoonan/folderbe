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

    def find_by_id(user_id) -> User:
        sql = "select * from User where id = {}".format(user_id)
        cursor = get_db().cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        return result


    def insert(user: User):
        sql = """insert into User (`name`, `img`, `email`) VALUES ("{}", "{}", "{}")""".format(user.name, user.user_img, user.email)
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