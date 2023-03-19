from flask import Blueprint, abort, g, make_response, redirect, request, session, url_for, Response
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from dotenv import load_dotenv

from .db.dao import ChannelDao, UserDao
from .db.model import User
from .oauth_api import get_whole_channels
import requests
import os
import time
import base64
import json
import copy


load_dotenv()
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtube.readonly"]

bp = Blueprint('auth', __name__, url_prefix='/auth')


def save_user_to_session(user):
    session['user_name'] = user.name
    session['user_email'] = user.email
    session['user_id'] = user.id
    session['user_img'] = user.user_img


def id_token_to_user(user_info: dict) -> User:
    user = UserDao.find_by(user_info['email'], key='email')
    if user is None:
        # 회원가입
        user = User(user_info)
        UserDao.insert(user)
    return user


def jwt_to_user(jwt):
    user_info = id_token.verify_oauth2_token(jwt, Request(), CLIENT_ID)
    user = id_token_to_user(user_info)
    save_user_to_session(user)

    UserDao.update(user)
    return user


def postprocess_user(response):
    if session.get('user_id') is None:
        user = jwt_to_user(response['id_token'])
    user = UserDao.find_by(session['user_id'])
    refresh_token = response.get('refresh_token')
    if refresh_token is None:  # 이 경우는 거의 없지만, 있어도 회원가입된 경우
        refresh_token = user.refresh_token
    user.refresh_token = refresh_token
    UserDao.update(user)
    
    channels = get_whole_channels()
    ChannelDao.insert_whole_channels(channels, user.id)


@bp.after_request
def after_api_auth(response: Response):  # 403으로 oauth 동의를 안 할 시
    if response.status_code == 403:
        return redirect(url_for("auth.authorize", prompt='consent'))
    return response


@bp.route("/authorize", methods=['GET', 'POST'])
def authorize():
    params = {"client_id": CLIENT_ID,
              "redirect_uri": url_for("auth.callback", _external=True, _scheme='https'),
              "response_type": "code",
              "scope": ' '.join(SCOPES),
              "access_type": "offline",
              "include_granted_scopes": 'true'}
    # 로그인 이후 요청 보낼 시
    if request.method == 'POST':
        jwt = request.form['credential']
        user = jwt_to_user(jwt)
        params.update({'login_hint': user.email})
    # 도중 토큰 만료, 재로그인 필요할 시
    prompt = request.args.get('prompt')
    if prompt is not None:
        params.update({'prompt': prompt})
    return redirect(requests.get(AUTHORIZATION_URL, params=params, allow_redirects=False).url)


@bp.route("/callback", methods=['GET', 'POST'])
def callback():
    params = {"code": request.args.get("code"),
              "client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET,
              "redirect_uri": url_for("auth.callback", _external=True, _scheme='https'),
              "grant_type": "authorization_code",
              "include_granted_scopes": 'true'}
    response = requests.post(TOKEN_URL, params=params).json()
    session.permanent = True
    session['expired_at'] = time.time() + response['expires_in']  # 토큰 만료시간 기입
    session['access_token'] = response['access_token']
    postprocess_user(response)
    return redirect(url_for("main.like_videos"))


# TODO: redirect을 원래 main이 아닌 원래 url로 보내기
@bp.route("/refresh_token")
def refresh_token():
    user = UserDao.find_by(session['user_id'])
    params = {"client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET,
              "refresh_token": user.refresh_token,
              "grant_type": "refresh_token"}
    response = requests.post(TOKEN_URL, params=params)
    if response.status_code != 200:
        return redirect(url_for("auth.authorize")) # refresh token도 만료 되면 재인증을 거쳐야함. 
    session.permanent = True
    response = response.json()
    session['access_token'] = response['access_token']  # 이 때 id_token도 같이 오긴 하네
    session['expired_at'] = time.time() + response['expires_in']  # 토큰 만료시간 기입

    postprocess_user(response)
    return redirect(url_for("main.like_videos"))
