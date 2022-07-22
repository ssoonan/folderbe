from flask import session, url_for, redirect
from .model import Channel, Video
import requests


SUBSCRIPTION_API_URL = "https://www.googleapis.com/youtube/v3/subscriptions"
SEARCH_API_URL = "https://www.googleapis.com/youtube/v3/search"
MAX_RESULTS = 50



def request_api(http_method, api_url, params):
    headers = {"Authorization": "Bearer " + session.get('access_token', '')}
    response = http_method(api_url, params=params, headers=headers)
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


def get_videos_from_channel(channel: Channel, max_results=15):
    params = {"part": "snippet", "channelId": channel.channel_id, "order": "date", "type": "video", "maxResults": max_results}
    response = request_api(requests.get, SEARCH_API_URL, params)
    videos = []
    for item in response['items']:
        video = Video(item['id']['videoId'], item['snippet']['thumbnails']['high']['url'], item['snippet']['title'], 0, item['snippet']['publishedAt'], 0, item['snippet']['description'], channel)
        videos.append(video)
    return videos
        
