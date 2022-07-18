import requests
import os

from flask import Flask, redirect, render_template, request, url_for, session
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap5

from model import Thumbnail


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


app = Flask(__name__, static_url_path='/static')
app.secret_key = "123asd2t234df!@#"
bootstrap = Bootstrap5(app)


def back_to_auth(response: requests.Response):
    if session.get('access_token') is None:  # access_token 자체가 없을 때
        return redirect("authorize")
    if response.status_code == 401:  # access_token이 있어도 인증이 안 될 때 -> refresh_token으로 재발급
        return redirect("refresh_token")


def request_api(http_method, api_url, params):
    headers = {"Authorization": "Bearer " + session.get('access_token', '')}
    response = http_method(api_url, params=params, headers=headers)
    if response.status_code != 200:
        return back_to_auth(response)
    return response.json()


@app.route("/index")
@app.route("/")
def index():
    example_thumbnail = Thumbnail("https://i.ytimg.com/vi/QmpTkkaKYSU/hqdefault.jpg", "j-hope '방화 (Arson)' Official MV", "10734349", "2022-07-15T03:59:09Z")
    folders = ["Eng", "ジム", "日本語", "coffee"]
    thumbnails = [example_thumbnail, example_thumbnail, example_thumbnail, example_thumbnail, example_thumbnail, example_thumbnail,
                  example_thumbnail, example_thumbnail, example_thumbnail, example_thumbnail, example_thumbnail, example_thumbnail]

    return render_template("index.html", folders=folders, thumbnails=thumbnails)



@app.route("/list")
def list():
    
    folders = ["Eng", "ジム", "日本語", "coffee"] # TODO: sidebar 데이터 중복 제거하기
    

    return render_template("list.html", folders=folders)


@app.route("/api_test")
def api_test():
    params = {"part": "snippet", "mine": True, "maxResults": 50}
    response = request_api(requests.get, API_URL, params)
    return response


@app.route("/authorize")
def authorize():
    params = {"client_id": CLIENT_ID,
              "redirect_uri": url_for("callback", _external=True),
              "response_type": "code",
              "scope": ' '.join(SCOPES),
              "access_type": "offline"}
    return redirect(requests.get(AUTHORIZATION_URL, params=params, allow_redirects=False).url)


@app.route("/callback")
def callback():
    params = {"code": request.args.get("code"),
              "client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET,
              "redirect_uri": url_for("callback", _external=True),
              "grant_type": "authorization_code"}
    response = requests.post(TOKEN_URL, params=params).json()
    session['access_token'] = response['access_token']
    session['refresh_token'] = response['refresh_token']
    return redirect("api_test")


@app.route("/refresh_token")
def refresh_token():
    params = {"client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET,
              "refresh_token": session.get('refersh_token', ''),
              "grant_type": "refresh_token"}
    response = requests.post(TOKEN_URL, params=params)
    if response.status_code != 200:
        return redirect("authorize") # refresh token도 만료 되면 재인증을 거쳐야함
    session['access_token'] = response.json()['access_token']
    return redirect("api_test")