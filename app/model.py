

class Channel:
    def __init__(self, channel_id, icon_img, name):
        self.channel_id = channel_id
        self.icon_img = icon_img
        self.name = name


class Folder:
    def __init__(self, name):
        self.name = name
        self.channels = []
    
    def add_channels(self, channels):
        self.channels.extend(channels)

    
class Video:
    def __init__(self, video_id, thumbnail_img, title, view_counts, published_date, likes, info, channel):
        self.video_id = video_id
        self.thumbnail_img = thumbnail_img
        self.title = title
        self.view_counts = view_counts
        self.published_date = published_date
        self.likes = likes
        self.info = info
        self.channel = channel