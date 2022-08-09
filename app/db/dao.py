from flask import g, current_ap
from typing import List


from app.model import Channel, Folder, User


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