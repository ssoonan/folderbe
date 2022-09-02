from typing import List

from .oauth_api import get_playlist_from_channel, get_videos_from_channel
from .db.dao import ChannelDao
from .db.model import Channel


def get_videos_from_channels(channels: List[Channel]):
    whole_videos = []
    for channel in channels:
        if not channel.playlist_id:
            get_playlist_from_channel(channel)
            ChannelDao.update_channel(channel)
        videos = get_videos_from_channel(channel, len(channels))
        whole_videos.extend(videos)
    whole_videos.sort(key=lambda video: video.published_date, reverse=True)
    return whole_videos