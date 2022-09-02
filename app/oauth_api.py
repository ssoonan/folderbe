from flask import jsonify, session, url_for, redirect, Response, abort
from .db.model import Channel, Video
import requests
import httpx
import asyncio
import time


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


async def async_http(http_method_name, url, json):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": "Bearer " + session.get('access_token', '')}
        http_method = getattr(client, http_method_name)
        response = await http_method(url, headers=headers, json=json)
        if response.status_code != 200:
            return abort(401)
        return response.json()


def request_api(http_method, api_url, params):
    headers = {"Authorization": "Bearer " + session.get('access_token', '')}
    response = http_method(api_url, params=params, headers=headers)
    if response.status_code != 200:
        return abort(401)
    return response.json()


async def request_test():
    a = time.time()
    urls = ["https://example.com/"] * 10
    results = []
    for url in urls:
        print("start")
        results.append(async_http('get', url))
    await asyncio.gather(*results)
    print(results)
    print(time.time() - a)


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


def get_playlist_from_channel(channel: Channel) -> str:
    params = {"part": "contentDetails", "id": channel.channel_id}
    response = request_api(requests.get, CHANNEL_API_URL, params)
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    channel.playlist_id = playlist_id


def get_videos_from_channel(channel: Channel, channel_counts):
    max_results = 18 // channel_counts + 1
    params = {"part": "snippet", "playlistId": channel.playlist_id, "maxResults": max_results}
    response = request_api(requests.get, PLAYLIST_API_URL, params)  # 0.4초..
    videos = []
    for item in response['items']:
        video = Video(item['snippet']['resourceId']['videoId'], item['snippet']['thumbnails']['high']['url'], item['snippet']['title'], 0, item['snippet']['publishedAt'], 0, item['snippet']['description'], channel)
        videos.append(video)
    return videos


def get_statistics_from_video(video_ids):
    video_ids = ','.join(video_ids)
    params = {"part": "statistics", "id": video_ids}
    response = request_api(requests.get, VIDEO_API_URL, params)  # 0.27초.. 이건 video id를 일단 받아야 하기 때문에 동기적으로 할 수 밖에 없긴 한데.. 일단 미루자


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