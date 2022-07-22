from flask import session, url_for, redirect
from .model import Channel
from .auth import API_URL
import requests



MAX_RESULTS = 50



def request_api(http_method, api_url, params):
    headers = {"Authorization": "Bearer " + session.get('access_token', '')}
    response = http_method(api_url, params=params, headers=headers) # TODO: 이 결과가 401일 때의 refresh_token 처리
    if response.status_code == 401:
        return redirect(url_for("auth.refresh_token"))
    return response.json()


def get_whole_channels():
    params = {"part": "snippet", "mine": True, "maxResults": MAX_RESULTS}
    response = request_api(requests.get, API_URL, params)
    channels = response['items']
    channel_instances = []

    if response.get("nextPageToken") is not None:
        params['pageToken'] = response['nextPageToken']
        response = request_api(requests.get, API_URL, params)
        channels.extend(response["items"])


    for channel in channels:
        channel_instance = Channel(channel['snippet']['thumbnails']['high']['url'], channel['snippet']['title'])
        channel_instances.append(channel_instance)
    
    return channel_instances