import requests
import time

from flask import Blueprint, redirect, render_template, url_for, session


from .model import Channel, Folder, Video
from .oauth_api import  get_videos_from_channel, get_whole_channels, request_api


bp = Blueprint('main', __name__, )


@bp.before_request
def check_access_token():
    if session.get('access_token') is None:  # access_token 자체가 없을 때
        return redirect(url_for("auth.authorize"))
    
    if time.time() > session['expired_at']:  # 현재 시간이 더 크면 만료된 것
        return redirect(url_for('auth.refresh_token'))



@bp.route("/index")
@bp.route("/")
def index():
    channels = get_whole_channels()
    whole_videos = []
    for channel in channels:
        videos = get_videos_from_channel(channel)
        whole_videos.extend(videos)
    whole_videos.sort(key=lambda video: video.published_date, reverse=True)  #TODO: 이 코드가 굳이 여기에 있어야 할까?

    folder = Folder("all")
    folder.add_channels(channels)
    folders = [folder]

    videos = whole_videos[:15]
    return render_template("index.html", folders=folders, videos=videos)



@bp.route("/list")
def list():
    
    folders = ["Eng", "ジム", "日本語", "coffee"] # TODO: sidebar 데이터 중복 제거하기
    

    return render_template("list.html", folders=folders)
