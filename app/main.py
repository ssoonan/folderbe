import requests
import os

from flask import Blueprint, Flask, redirect, render_template, request, url_for, session
from dotenv import load_dotenv


from .model import Channel, Folder, Video
from .oauth_api import API_URL, get_whole_channels, request_api


bp = Blueprint('main', __name__, )


@bp.before_request
def check_access_token():
    if session.get('access_token') is None:  # access_token 자체가 없을 때
        return redirect(url_for("auth.authorize"))


@bp.route("/index")
@bp.route("/")
def index():
    channels = get_whole_channels()

    example_channel = Channel("https://yt3.ggpht.com/ytc/AKedOLRRjGuN-GPWubsrcVN8jyhnELYRIfWG03gBR7fGrg=s68-c-k-c0x00ffffff-no-rj", "HYBE LABELS")
    example_video = Video("https://i.ytimg.com/vi/QmpTkkaKYSU/hqdefault.jpg", "j-hope '방화 (Arson)' Official MV", 10734349, "2022-07-15T03:59:09Z", 0, "", example_channel)
    folder = Folder("all")
    folder.add_channels(channels)
    folders = [folder]

    videos = [example_video, example_video, example_video, example_video, example_video, example_video,
                  example_video, example_video, example_video, example_video, example_video, example_video]



    return render_template("index.html", folders=folders, videos=videos)



@bp.route("/list")
def list():
    
    folders = ["Eng", "ジム", "日本語", "coffee"] # TODO: sidebar 데이터 중복 제거하기
    

    return render_template("list.html", folders=folders)


@bp.route("/api_test")
def api_test():
    params = {"part": "snippet", "mine": True, "maxResults": 50}
    response = request_api(requests.get, API_URL, params)
    return response
