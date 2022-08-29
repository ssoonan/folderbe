import time
import asyncio
import httpx

from flask import Blueprint, redirect, render_template, url_for, session, g, \
    request, jsonify, Response


from .model import Channel, Folder, LikeFolder, Video, make_example_videos
from .oauth_api import  get_liked_videos, get_playlist_from_channel, get_videos_from_channel, get_whole_channels, request_api
from .db.dao import ChannelDao, FolderDao, UserDao


bp = Blueprint('main', __name__, )


@bp.before_request
def check_access_token():
    if session.get('access_token') is None:  # access_token 자체가 없을 때
        return redirect(url_for("auth.authorize"))
    
    if time.time() > session['expired_at']:  # 현재 시간이 더 크면 만료된 것
        return redirect(url_for('auth.refresh_token'))
    
    user = UserDao.find_by(session['user_id'], key="id")
    folders = FolderDao.find_by_user(user)
    folders.insert(0, LikeFolder())
    g.user = user
    g.folders = folders


@bp.after_request
def after_api_auth(response: Response):
    if response.status_code == 401:
        return redirect(url_for("auth.authorize"))
    return response
    

@bp.route("/index")
@bp.route("/")
def index():
    videos = get_liked_videos()
    return render_template("index.html", videos=videos)


@bp.route("/index/<folder_id>")
@bp.route("/<folder_id>")
def folder_videos(folder_id):
    if folder_id == '-1':
        videos = get_liked_videos()
        return render_template("index.html", videos=videos)
    # channels = []
    # for folder in g.folders:
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
    # return render_template("index.html", videos=videos)


@bp.route("/folder_list")
def list():
    channels = ChannelDao.find_channels_from_user(g.user)
    return render_template("list.html", channels=channels)


@bp.route("/folder_list", methods=['POST'])
def create_folder():
    folder_name = request.form['folder_name']
    result = FolderDao.insert(Folder(folder_name, session['user_id']))
    if not result:
        return jsonify({"message": "중복된 이름"}), 400
    return jsonify({"message": "success"})


@bp.route("/folder_list", methods=["DELETE"])
def delete_folder():
    folder_id = request.json.get('id')
    result = FolderDao.delete(folder_id)
    if not result:
        return jsonify({"message": "error"}), 400
    return jsonify({"message": "success"})


@bp.route("/insert_channels", methods=["POST"])
def insert_channel():
    channel_ids = request.form.getlist('channel')
    folder_id = request.form['folderId']
    ChannelDao.insert_channels_for_folder(channel_ids, folder_id)
    return jsonify({"message": "success"})