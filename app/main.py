import requests
import time

from flask import Blueprint, redirect, render_template, url_for, session, g


from .model import Channel, Folder, Video, make_example_videos
from .oauth_api import  get_liked_videos, get_playlist_from_channel, get_videos_from_channel, get_whole_channels, request_api
from .db.dao import FolderDao, UserDao


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
    user = UserDao.find_by(session['user_id'], key="id")
    folders = FolderDao.find_by_user(user)
    if not folders:
        folders = [Folder('좋아요 표시한 동영상', None)]
        videos = get_liked_videos()
        return render_template("index.html", folders=folders, videos=videos)
    # channels = []
    # for folder in folders:
    #     channels.extend(folder.channels)
    # for channel in channels:
    # channels = get_whole_channels()
    # whole_videos = []
    # for channel in channels[2:5]:
    #     get_playlist_from_channel(channel)
    #     videos = get_videos_from_channel(channel)
    #     whole_videos.extend(videos)
    # whole_videos.sort(key=lambda video: video.published_date, reverse=True)  #TODO: 이 코드가 굳이 여기에 있어야 할까?

    # videos = whole_videos[:15]

    



@bp.route("/list")
def list():
    
    folders = ["Eng", "ジム", "日本語", "coffee"] # TODO: sidebar 데이터 중복 제거하기
    

    return render_template("list.html", folders=folders)
