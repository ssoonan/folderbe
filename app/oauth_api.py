from distutils.command.upload import upload
from flask import jsonify, session, url_for, redirect
from .model import Channel, Video
import requests


SUBSCRIPTION_API_URL = "https://www.googleapis.com/youtube/v3/subscriptions"
CHANNEL_API_URL = "https://www.googleapis.com/youtube/v3/channels"
PLAYLIST_API_URL = "https://www.googleapis.com/youtube/v3/playlistItems"

MAX_RESULTS = 50



def request_api(http_method, api_url, params):
    headers = {"Authorization": "Bearer " + session.get('access_token', '')}
    response = http_method(api_url, params=params, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": {"message": "quota excedded"}})  # TODO: 403 에러 처리 
    return response.json()


def get_whole_channels():
    params = {"part": "snippet", "mine": True, "maxResults": MAX_RESULTS}
    response = request_api(requests.get, SUBSCRIPTION_API_URL, params)
    channels = response['items']
    channel_instances = []

    if response.get("nextPageToken") is not None: # MAX_RESULT 개수 이상일 때 -> 나머지도 다 자겨옴
        params['pageToken'] = response['nextPageToken']
        response = request_api(requests.get, SUBSCRIPTION_API_URL, params)
        channels.extend(response["items"])


    for channel in channels:
        channel_instance = Channel(channel['snippet']['resourceId']['channelId'], channel['snippet']['thumbnails']['high']['url'], channel['snippet']['title'])
        channel_instances.append(channel_instance)
    
    return channel_instances


def get_playlist_from_channel(channel: Channel):
    params = {"part": "contentDetails", "id": channel.channel_id}
    response = request_api(requests.get, CHANNEL_API_URL, params)
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    channel.set_playlist_id(playlist_id)


def get_videos_from_channel(channel: Channel, max_results=15):
    params = {"part": "snippet", "playlistId": channel.playlist_id, "maxResults": max_results}
    response = request_api(requests.get, PLAYLIST_API_URL, params)
    videos = []
    for item in response['items']:
        video = Video(item['snippet']['resourceId']['videoId'], item['snippet']['thumbnails']['high']['url'], item['snippet']['title'], 0, item['snippet']['publishedAt'], 0, item['snippet']['description'], channel)
        videos.append(video)
    return videos
