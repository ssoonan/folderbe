

class Channel:
    def __init__(self, icon_img, name, link):
        self.icon_img = icon_img
        self.name = name
        self.link = link


class Folder:
    def __init__(self, name):
        self.name = name
        self.channels = []

    
class Video:
    def __init__(self, thumbnail_img, title, view_counts, published_date, likes, info, channel):
        self.thumbnail_img = thumbnail_img
        self.title = title
        self.view_counts = view_counts
        self.published_date = published_date
        self.likes = likes
        self.info = info
        self.channel = channel