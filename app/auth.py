from flask import Blueprint, redirect, request, session, url_for
from dotenv import load_dotenv
import requests
import os
import time


load_dotenv()
API_URL = "https://www.googleapis.com/youtube/v3/subscriptions"
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/youtubepartner"]



bp = Blueprint('auth', __name__, url_prefix='/auth')


def back_to_auth(response: requests.Response):
    if session.get('access_token') is None:  # access_token 자체가 없을 때
        return redirect("authorize")
    if response.status_code == 401:  # access_token이 있어도 인증이 안 될 때 -> refresh_token으로 재발급
        return redirect("refresh_token")



# if response.status_code == 401 or response.status_code == 403:  # TODO: refresh_token을 쓰는 부분까지 말끔하게 연결이.. access_token이 있어도 인증이 안 될 때 -> refresh_token으로 재발급

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
    return redirect(url_for("main.index"))


@bp.route("/refresh_token")
def refresh_token():
    params = {"client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET,
              "refresh_token": session.get('refresh_token', ''),
              "grant_type": "refresh_token"}
    response = requests.post(TOKEN_URL, params=params)
    if response.status_code != 200:
        return redirect(url_for("auth.authorize")) # refresh token도 만료 되면 재인증을 거쳐야함
    session['access_token'] = response.json()['access_token']
    session['expired_at'] = time.time() + response.json()['expires_in']  # 토큰 만료시간 기입
    return redirect(url_for("main.index"))