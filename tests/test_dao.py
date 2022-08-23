from app.db.dao import FolderDao, UserDao
from app.model import Folder, User
from flask import Flask


def test_user_dao(app: Flask):
    with app.app_context():
        email = 'asd@gmail.com'
        UserDao.insert(User('https://lh3.googleusercontent.com/a-/AFdZucpJYYcRKM4NmcwxOTsRh29eRdvpRCheNfKj0o6KRw=s96-c-rg-br100', '옥순환', email))
        user1 = UserDao.find_by(email, key='email')
        assert type(user1) == User
        assert user1.name == '옥순환'
        
        user1.refresh_token = "after token"
        UserDao.update(user1)  # update 파트
        assert UserDao.find_by(email, key="email").refresh_token == "after token"


def test_folder_dao(app: Flask):
    with app.app_context():
        email = 'asd2@gmail.com'
        user1 = User('https://lh3.googleusercontent.com/a-/AFdZucpJYYcRKM4NmcwxOTsRh29eRdvpRCheNfKj0o6KRw=s96-c-rg-br100', '옥순환', email)
        UserDao.insert(user1)
        folder1 = Folder("테스트폴더1", user1.user_id)
        folder2 = Folder("테스트폴더2", user1.user_id)
        FolderDao.insert(folder1)
        FolderDao.insert(folder2)
        folders = FolderDao.find_by_user(user1)
        assert folders[0].user_id == user1.user_id
        assert folders[1].user_id == user1.user_id
        assert "테스트폴더1" in [folder.name for folder in folders]
        assert "테스트폴더2" in [folder.name for folder in folders]

        FolderDao.delete(folder1)
        FolderDao.delete(folder2)
        folders = FolderDao.find_by_user(user1)
        assert "테스트폴더1" not in [folder.name for folder in folders]
        assert "테스트폴더2" not in [folder.name for folder in folders]


