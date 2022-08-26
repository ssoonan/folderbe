from flask import Blueprint, redirect, request, session, url_for, Response
from dotenv import load_dotenv

from .db.dao import ChannelDao, UserDao
from .model import User
from .oauth_api import get_whole_channels
import requests
import os
import time
import base64
import json


load_dotenv()
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/youtubepartner",
          "https://www.googleapis.com/auth/userinfo.profile",
          "https://www.googleapis.com/auth/userinfo.email"]

bp = Blueprint('auth', __name__, url_prefix='/auth')


def parse_id_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise Exception("Incorrect id token format")

    payload = parts[1]
    padded = payload + '=' * (4 - len(payload) % 4)
    decoded = base64.b64decode(padded)
    return json.loads(decoded)


def id_token_to_user(user_info, refresh_token) -> User:
    user_name = user_info['name']
    user_img = user_info['picture']
    user_email = user_info['email']
    user = UserDao.find_by(user_email, key='email')
    if user is None:
        user = User(user_img, user_name, user_email, refresh_token)
        UserDao.insert(user)
    else:  # TODO: 업데이트 하는 게 너무 장황한데?
        user.user_img = user_img
        user.refresh_token = refresh_token
        UserDao.update(user)
    session['user_name'] = user_name
    session['user_email'] = user_email
    session['user_id'] = user.user_id
    session['user_img'] = user_img
    return user


@bp.route("/authorize")
def authorize():
    params = {"client_id": CLIENT_ID,
              "redirect_uri": url_for("auth.callback", _external=True),
              "response_type": "code",
              "scope": ' '.join(SCOPES),
              "access_type": "offline"}
    return redirect(requests.get(AUTHORIZATION_URL, params=params, allow_redirects=False).url)


@bp.route("/callback")
def callback():
    params = {"code": request.args.get("code"),
              "client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET,
              "redirect_uri": url_for("auth.callback", _external=True),
              "grant_type": "authorization_code"}
    response = requests.post(TOKEN_URL, params=params).json()
    session.permanent = True
    session['expired_at'] = time.time() + response['expires_in']  # 토큰 만료시간 기입
    session['access_token'] = response['access_token']
    session['refresh_token'] = response['refresh_token']

    # 회원가입 확인
    user_info = parse_id_token(response['id_token'])
    user = id_token_to_user(user_info, response['refresh_token'])
    
    channels = get_whole_channels()
    ChannelDao.insert_whole_channels(channels, user)
    return redirect(url_for("main.index"))

# TODO: 1. refresh 토큰 session이 아닌 DB에서 2. redirect을 원래 main이 아닌 원래 url로 보내기
@bp.route("/refresh_token")
def refresh_token():
    params = {"client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET,
              "refresh_token": session.get('refresh_token', ''),
              "grant_type": "refresh_token"}
    response = requests.post(TOKEN_URL, params=params)
    if response.status_code != 200:
        return redirect(url_for("auth.authorize")) # refresh token도 만료 되면 재인증을 거쳐야함. 
    session.permanent = True
    response = response.json()
    session['access_token'] = response['access_token']  # 이 때 id_token도 같이 오긴 하네
    session['expired_at'] = time.time() + response['expires_in']  # 토큰 만료시간 기입

    user_info = parse_id_token(response['id_token'])
    user = id_token_to_user(user_info, session.get('refresh_token', ''))
    
    channels = get_whole_channels()
    ChannelDao.insert_whole_channels(channels, user)
    return redirect(url_for("main.index"))