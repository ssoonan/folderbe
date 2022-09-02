import asyncio
import time
from typing import List

from .oauth_api import get_playlist_from_channel, get_videos_from_channels, async_get_videos_from_channel
from .db.dao import ChannelDao
from .db.model import Channel, Video


# def get_videos_from_channels(channels: List[Channel]):
#     whole_videos = []
#     a = time.time()
#     for channel in channels:
#         if not channel.playlist_id:
#             get_playlist_from_channel(channel)
#             ChannelDao.update_channel(channel)
#         videos = get_videos_from_channel(channel, len(channels))
#         whole_videos.extend(videos)
#     whole_videos.sort(key=lambda video: video.published_date, reverse=True)
#     print("time: ", time.time() - a)
#     return whole_videos


async def check_playlist_id_and_get_videos_from_channels(channels: List[Channel]):
    for channel in channels:
        if not channel.playlist_id:
            get_playlist_from_channel(channel)
            ChannelDao.update_channel(channel)
    return await get_videos_from_channels(channels)