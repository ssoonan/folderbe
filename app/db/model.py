
class User:
    def __init__(self, user_info):
        self.user_img = user_info.get('img') or user_info.get('picture')
        self.name = user_info['name']
        self.email = user_info['email']
        self.refresh_token = user_info.get('refresh_token')
        self.id = user_info.get('id') or user_info.get('sub')
    
    def __repr__(self) -> str:
        return "user_{}".format(self.name)


class Channel:
    def __init__(self, channel_id, icon_img, name, playlist_id=None, folder_ids=[]):
        self.channel_id = channel_id
        self.icon_img = icon_img
        self.name = name
        self.playlist_id = playlist_id
        self.folder_ids = folder_ids

    def __repr__(self) -> str:
        return "channel_{}".format(self.name)


class Folder:
    def __init__(self, name, user_id=None, folder_id=None):
        self.name = name
        self.channels = []
        self.user_id = user_id
        self.folder_id = folder_id
    
    def add_channels(self, channels):
        self.channels.extend(channels)
    
    def __repr__(self) -> str:
        return "folder_{}".format(self.name)


class LikeFolder(Folder):
    def __init__(self, name="좋아요 동영상", folder_id=-1):
        super().__init__(name, folder_id=folder_id)

    
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
    
    def get_video_url(self):
        return "https://www.youtube.com/embed/{}".format(self.video_id)
    
    def to_dict(self):
        result = self.__dict__
        result['channel'] = self.channel.__dict__
        return result

    def __repr__(self) -> str:
        return "video_{}".format(self.title)


def make_example_videos():
    example_channel1 = Channel("asd", "https://yt3.ggpht.com/ytc/AKedOLRRjGuN-GPWubsrcVN8jyhnELYRIfWG03gBR7fGrg=s68-c-k-c0x00ffffff-no-rj", "HYBE LABELS")
    example_video = Video("1RJvz1fwy8E", "https://i.ytimg.com/vi/QmpTkkaKYSU/hqdefault.jpg", "j-hope '방화 (Arson)' Official MV", 10734349, "2022-07-15T03:59:09Z", 0, "", example_channel1)
    example_channel2 = Channel("asd", "https://yt3.ggpht.com/ytc/AKedOLSTz7hqk6t2kUEgGF5Ote28_wirhNLfwfgHBzWTvw=s88-c-k-c0x00ffffff-no-rj", "백종원의 요리비책 Paik's Cuisine")
    example_video2 = Video("FJfLo9PSntY", "https://i.ytimg.com/vi/FJfLo9PSntY/hqdefault.jpg?sqp=-oaymwEcCPYBEIoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCGNRIP33dbJUP3XwQEca6dxOJJ1g", 
    "제작진놈들의 계속되는 캠핑 강행군에 탈출을 시도하는 도시러버 백종원의 모습입니다", 0, "2022-07-22T14:55:09Z", 0, "", example_channel2)
    folder = Folder("all")
    folders = [folder]

    videos = [example_video, example_video2, example_video, example_video2, example_video, example_video2,
                example_video, example_video2, example_video, example_video2, example_video2, example_video]
    
    return folders, videos