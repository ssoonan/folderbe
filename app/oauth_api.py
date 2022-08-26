from flask import jsonify, session, url_for, redirect, Response, abort
from .model import Channel, Video
import requests


SUBSCRIPTION_API_URL = "https://www.googleapis.com/youtube/v3/subscriptions"
CHANNEL_API_URL = "https://www.googleapis.com/youtube/v3/channels"
PLAYLIST_API_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
VIDEO_API_URL = "https://www.googleapis.com/youtube/v3/videos"

MAX_RESULTS = 50


def truncate_views(view_counts):
    view_counts = int(view_counts)
    if 1000 <= view_counts < 10000:  # 천
        view_counts *= 1e-3
        view_counts = round(view_counts, 1)
        view_counts = str(view_counts) + '천'
    elif 10000 <= view_counts < 100000:  # 만
        view_counts *= 1e-4
        view_counts = round(view_counts, 1)
        view_counts = str(view_counts) + '만'
    elif 10000 <= view_counts < 1000000:  # 10만 ~ 백만
        view_counts *= 1e-4
        view_counts = round(view_counts, 0)
        view_counts = str(int(view_counts)) + '만'
    elif 100000 <= view_counts < 10000000:  # 백만 ~ 천만
        view_counts *= 1e-4
        view_counts = round(view_counts, 0)
        view_counts = str(int(view_counts)) + '만'
    elif 1000000 <= view_counts < 100000000:  # 천만 ~ 억
        view_counts *= 1e-4
        view_counts = round(view_counts, 0)
        view_counts = str(int(view_counts)) + '만'
    elif 10000000 <= view_counts < 1000000000:  # 억 ~ 10억
        view_counts *= 1e-8
        view_counts = round(view_counts, 1)
        view_counts = str(view_counts) + '억'
    elif 100000000 <= view_counts < 10000000000:  # 10억 ~ 100억
        view_counts *= 1e-8
        view_counts = round(view_counts, 0)
        view_counts = str(int(view_counts)) + '억'
    
    return view_counts


def request_api(http_method, api_url, params):
    headers = {"Authorization": "Bearer " + session.get('access_token', '')}
    response = http_method(api_url, params=params, headers=headers)
    if response.status_code != 200:
        return abort(401)
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


def get_videos_from_channel(channel: Channel, max_results=18):
    params = {"part": "snippet", "playlistId": channel.playlist_id, "maxResults": max_results}
    response = request_api(requests.get, PLAYLIST_API_URL, params)
    videos = []
    for item in response['items']:
        video = Video(item['snippet']['resourceId']['videoId'], item['snippet']['thumbnails']['high']['url'], item['snippet']['title'], 0, item['snippet']['publishedAt'], 0, item['snippet']['description'], channel)
        videos.append(video)
    return videos


def get_liked_videos(max_results=18):
    params = {"part": "snippet,statistics", "myRating": "like", "maxResults": max_results}
    response = request_api(requests.get, VIDEO_API_URL, params)
    videos = []
    for item in response['items']:
        video = Video(item['id'], item['snippet']['thumbnails']['high']['url'], item['snippet']['title'], truncate_views(item['statistics']['viewCount']), item['snippet']['publishedAt'].split('T')[0], 
                      item['statistics']['likeCount'], item['snippet']['description'], 
                      Channel(item['snippet']['channelId'], None, item['snippet']['channelTitle'], None))
        videos.append(video)
    return videos