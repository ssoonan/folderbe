import asyncio
from typing import List

from .oauth_api import get_playlist_from_channel, async_get_videos_from_channel
from .db.dao import ChannelDao
from .db.model import Channel, Video


async def async_get_videos_from_channels(channels: List[Channel]):
    responses = []
    for channel in channels:
        response = async_get_videos_from_channel(channel, len(channels))
        responses.append(response)
    results = await asyncio.gather(*responses)
    whole_videos = []
    for result, channel in zip(results, channels):
        videos = []
        for item in result['items']:
            video = Video(item['snippet']['resourceId']['videoId'], item['snippet']['thumbnails']['high']['url'], item['snippet']['title'], 0, item['snippet']['publishedAt'], 0, item['snippet']['description'], channel)
            videos.append(video)
        whole_videos.extend(videos)
    whole_videos.sort(key=lambda video: video.published_date, reverse=True)
    return whole_videos



async def check_playlist_id_and_get_videos_from_channels(channels: List[Channel]):
    for channel in channels:
        if not channel.playlist_id:
            get_playlist_from_channel(channel)
            ChannelDao.update_channel(channel)
    return await async_get_videos_from_channels(channels)