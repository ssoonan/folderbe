import imp
from flask import Blueprint, redirect, request, session, url_for
from dotenv import load_dotenv

from app.db.dao import UserDao
from .model import User
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
    session['expired_at'] = time.time() + response['expires_in']  # 토큰 만료시간 기입
    session['access_token'] = response['access_token']
    session['refresh_token'] = response['refresh_token']

    # 회원가입 확인
    user_info = parse_id_token(response['id_token'])
    user_name = user_info['name']
    user_img = user_info['picture']
    user_email = user_info['email']
    user = UserDao.find_by(user_email, key='email')
    if user is None:
        user = User(user_img, user_name, user_email, response['refresh_token'])
        UserDao.insert(user)
    else:  # TODO: 업데이트 하는 게 너무 장황한데?
        user.user_img = user_img
        user.refresh_token = response['refresh_token']
        UserDao.update(user)
    session['user_name'] = user_name
    session['user_img'] = user_img
    
    return redirect(url_for("main.index"))


@bp.route("/refresh_token")
def refresh_token():
    params = {"client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET,
              "refresh_token": session.get('refresh_token', ''),
              "grant_type": "refresh_token"}
    response = requests.post(TOKEN_URL, params=params)
    if response.status_code != 200:
        return redirect(url_for("auth.authorize")) # refresh token도 만료 되면 재인증을 거쳐야함. 
    session['access_token'] = response.json()['access_token']  # 이 때 id_token도 같이 오긴 하네
    session['expired_at'] = time.time() + response.json()['expires_in']  # 토큰 만료시간 기입
    return redirect(url_for("main.index"))