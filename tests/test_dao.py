from app.db.dao import UserDao
from app.model import User
from flask import Flask


def test_user_dao(app: Flask):
    with app.app_context():
        email = 'asd@gmail.com'
        UserDao.insert(User('https://lh3.googleusercontent.com/a-/AFdZucpJYYcRKM4NmcwxOTsRh29eRdvpRCheNfKj0o6KRw=s96-c-rg-br100', '옥순환', email))
        user1 = UserDao.find_by(email, key='email')
        assert type(user1) == User
        assert user1.name == '옥순환'
        