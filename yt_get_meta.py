import csv
import re
from datetime import datetime

from youtube_api import YouTubeDataAPI


class YTMeta:
    def __init__(self, _api_key):
        self.api_key = _api_key
        self.yt = YouTubeDataAPI(self.api_key)

    @staticmethod
    def get_video_id(url):
        """
        Get ID from YT Video
        :param url:
        :type url: str
        :return: video_id
        :rtype: str
        """
        video_id = re.split('\?v=|&', url)[1]
        return video_id

    @staticmethod
    def get_playlist_id(url):
        """
        Get ID from YT Playlist
        :param url: YT Playlist URL
        :type url: str
        :return: YT Playlist ID
        :rtype: str
        """
        playlist_id = url.split('list=')[1]
        return playlist_id

    @staticmethod
    def video_meta_writer(res_dict, res_file):
        """
        Writes got video meta to a CSV file
        :param res_dict: A dict with metadata (video URL is a key)
        :type res_dict: dict
        :param res_file: result filename
        :type res_file: str
        :return:
        """
        with open(res_file, 'w', encoding='utf-8', newline='') as f:
            my_csv = csv.writer(f, delimiter='\t')
            heading = ['url', 'video_view_count', 'video_comment_count', 'video_like_count', 'video_dislike_count',
                       'video_publish_date', 'video_title', 'video_description', 'video_tags', 'video_thumbnail',
                       'channel_title', 'channel_id']
            my_csv.writerow(heading)

            for key in res_dict.keys():
                date = datetime.fromtimestamp(res_dict[key]['video_publish_date']).strftime('%Y-%m-%d')

                my_csv.writerow([key, res_dict[key]['video_view_count'], res_dict[key]['video_comment_count'],
                                 res_dict[key]['video_like_count'], res_dict[key]['video_dislike_count'],
                                 date, res_dict[key]['video_title'],
                                 res_dict[key]['video_description'], res_dict[key]['video_tags'],
                                 res_dict[key]['video_thumbnail'], res_dict[key]['channel_title'],
                                 res_dict[key]['channel_id']])

    def get_videos_from_playlist_id(self, playlist_url):
        """
        Gets video IDs from YT Playlist and returns a list with video URLs
        :param playlist_url: YT Playlist URL
        :type playlist_url: str
        :return: All URLs in Playlist
        :rtype: list
        """
        playlist_id = self.get_playlist_id(playlist_url)
        response = self.yt.get_videos_from_playlist_id(playlist_id)
        urls = []
        for elem in response:
            for key in elem.keys():
                if key == 'video_id':
                    urls.append(f'https://youtube.com/watch?v={elem[key]}')
        return urls

    def get_video_meta(self, video_id):
        """
        Gets video meta by video ID
        :param video_id:
        :type video_id: str
        :return: video meta
        :rtype: dict
        """
        try:
            get_meta = self.yt.get_video_metadata(video_id)
            return get_meta
        except Exception as e:
            print('Get video meta error: ', video_id, e, type(e))

    def worker(self, urls, res_file):
        """
        Worker
        :param urls: video URLs to parse
        :type urls: list
        :param res_file: csv result output file name
        :type res_file: str
        :return:
        """
        result = {}
        for url in urls:
            video_id = self.get_video_id(url)
            video_meta = self.get_video_meta(video_id)
            result[url] = video_meta
        self.video_meta_writer(result, res_file)

        print('Done! Check: ', res_file)


if __name__ == '__main__':
    api_key = input('Enter your API Key: ').strip()
    yt_meta = YTMeta(api_key)

    while True:
        work_mode = input('Choose one of the modes below: \n'
                          '1 - Parse by URLs list from .txt file\n'
                          '2 - Parse all videos by a playlist URL\n')

        if work_mode == '1':
            urls_file = input('Enter a URLs list file name: ').strip()
            urls_list = []
            with open(urls_file, 'r', encoding='utf-8') as f:
                for line in f:
                    urls_list.append(line.strip())
            break

        elif work_mode == '2':
            playlist = input('Enter a playlist URL: ').strip()
            urls_list = yt_meta.get_videos_from_playlist_id(playlist)
            break
        else:
            print('Please choose a correct number (1 or 2)\n')

    yt_meta.worker(urls_list, 'result.csv')
