import time
import asyncio
import httpx

from flask import Blueprint, redirect, render_template, url_for, session, g, \
    request, jsonify, Response, abort


from .db.model import Channel, Folder, LikeFolder, Video, make_example_videos
from .oauth_api import  get_liked_videos, get_whole_channels
from .db.dao import ChannelDao, FolderDao, UserDao
from .service import check_playlist_id_and_get_videos_from_channels


bp = Blueprint('main', __name__, )


@bp.before_request
def check_access_token():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for("auth.authorize")) # 둘 다 없는 쿠키 초기화 -> 인증
    if time.time() > session['expired_at']:  # 현재 시간이 더 크면 만료된 것
        return redirect(url_for('auth.refresh_token',  _external=True, _scheme='https'))  # session이 살아있으면 refresh_token
    user_id = session['user_id']
    user = UserDao.find_by(user_id) 
    if user is None: # 이 경우는 인가가 안 된 것이 아닌 forbid
        abort(403)
    folders = FolderDao.find_by_user(user_id)
    folders.insert(0, LikeFolder())
    g.folders = folders
    g.user_id = user_id


@bp.after_request
def after_api_auth(response: Response):  # 403으로 oauth 동의를 안 할 시
    if response.status_code == 403:
        return redirect(url_for("auth.authorize", prompt='consent'))
    return response


def check_folder_user(folder_id):  # TODO: 이걸 매번하는 방법이 없나? folder를 매번 쓰는 게 아니니까,,?
    folder = FolderDao.find_by_id(folder_id)
    if folder.user_id != g.user_id:
        abort(403)

@bp.route("/index")
@bp.route("/")
def index():
    videos = get_liked_videos()
    return render_template("index.html", videos=videos)


@bp.route("/folders/<folder_id>")
def folder_videos(folder_id):
    if folder_id == '-1':
        videos = get_liked_videos()
        return render_template("index.html", videos=videos)
    check_folder_user(folder_id)
    channels = ChannelDao.find_channels_from_folder(folder_id)
    videos = asyncio.run(check_playlist_id_and_get_videos_from_channels(channels))
    return render_template("index.html", videos=videos)


@bp.route("/folders")
def folders():
    # channels = get_whole_channels()  # TODO: 이걸 매번 안 날리고도 속도 개선할 방법이 필요
    # ChannelDao.insert_whole_channels(channels, g.user_id)
    channels = ChannelDao.find_channels_from_user(g.user_id)
    return render_template("list.html", channels=channels)


@bp.route("/folders", methods=['POST'])
def create_folder():
    folder_name = request.form['folder_name']
    result = FolderDao.insert(Folder(folder_name, g.user_id))
    if not result:
        return jsonify({"message": "중복된 이름"}), 400
    return jsonify({"message": "success"})


@bp.route("/folders", methods=["DELETE"])
def delete_folder():
    folder_id = request.json.get('id')
    check_folder_user(folder_id)
    result = FolderDao.delete(folder_id)
    if not result:
        return jsonify({"message": "error"}), 400
    return jsonify({"message": "success"})


@bp.route("/folder/<folder_id>/")
def channels_from_folder(folder_id):
    check_folder_user(folder_id)
    channels = ChannelDao.find_channels_from_folder(folder_id)
    channel_ids = [channel.channel_id for channel in channels]
    return jsonify({"channel_ids": channel_ids})


@bp.route("/folder/<folder_id>/", methods=['POST'])
def insert_channel_from_folder(folder_id):
    check_folder_user(folder_id)
    channel_id = request.json.get('channel_id')
    ChannelDao.insert_channel_for_folder(channel_id, folder_id)
    return jsonify({"message": "success"})


@bp.route("/folder/<folder_id>/", methods=['DELETE'])
def delete_channel_from_folder(folder_id):
    check_folder_user(folder_id)
    channel_id = request.json.get('channel_id')
    ChannelDao.delete_channel_from_folder(channel_id, folder_id)
    return jsonify({"message": "success"})

