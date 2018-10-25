from enum import Enum
import json
import random
import requests
import sys
sys.path.append("..")
import util.logger as logger
import util.settings as settings

class MediaType(Enum):
    """ MediaTypes """
    IMAGE = "Image"
    VIDEO = "Video"
    UNDEFINED = "Undefined"

class Post():
    def __init__(self, postId, title, mediaType, media, size, tag, views, ups, downs):
        self.postId = postId
        self.title = title
        self.mediaType = mediaType
        self.media = media
        self.size = size
        self.views = views
        self.ups = ups
        self.downs = downs
        self.tag = tag

class Imgur():
    """ Imgur class """
    def __init__(self, logger, setting):
        self.authenticated = False
        self.logger = logger
        self.setting = setting
    
    def authenticate(self):
        """ Autenticate the user """
        req = requests.get(self.setting.authLink, headers=self.setting.imgurHeaders)
        try:
            if req.json()['status'] == 200:
                self.logger.log(logger.LogLevel.INFO, 'Imgur authenticated successfully')
                return True
            else:
                self.logger.log(logger.LogLevel.ERROR, 'Failed to authenticate imgur. Status: %d' % (req.json()['status']))
                return False
        except Exception as e:
            self.logger.log(logger.LogLevel.CRITICAL, 'imgur authenticate exception: %s' % e)    
            return False

    def get_posts(self):
        """ Get all possible posts to tweet """
        postList = []
        for tag in self.setting.imgurTags:
            try:
                req = requests.get('%s%s' % (self.setting.tagLink, tag), headers=self.setting.imgurHeaders)
                for post in req.json()['data']['items']:
                    p = self.json_to_post(post, tag)
                    if p is not None:
                        postList.append(p)
            except Exception as e:
                self.logger.log(logger.LogLevel.CRITICAL, 'imgur.get_posts exception(%s): %s' % (tag, e))
        return postList
    
    def get_media_type(self, media):
        if media == 'image/jpeg' or media == 'image/png':
            return MediaType.IMAGE
        elif media == 'video/mp4' or media == 'image/gif':
            return MediaType.VIDEO
        else:
            return MediaType.UNDEFINED

    def get_value(self, post, indices):
        """ Gets value from an imgur json from tag, returns value """
        try:
            result = post
            for indice in indices:
                result = result[indice]
            return result
        except Exception as e:
            return None

    def json_to_post(self, post, tag):
        """ Converts json of a post, to a imgur.Post object """
        # Get media type (image/video)
        mediaType = self.get_value(post, ("images", 0, "type"))
        if mediaType is None:
            mediaType = self.get_value(post, ("type", ))
        mediaType = self.get_media_type(mediaType)

        imageCount = self.get_value(post, ('images_count',))
        if imageCount is None:
            imageCount = 1
        
        # Only want 1 image/video
        if imageCount > 1:
            return None
        
        # Get media url and size
        if mediaType == MediaType.IMAGE:
            media = self.get_value(post, ('images', 0, 'id', ))
            size = self.get_value(post, ('size', ))
            if size is None:
                size = self.get_value(post, ('images', 0, 'size', ))
            if media is None:
                media = self.get_value(post, ('link', ))
        elif mediaType == MediaType.VIDEO:
            media = self.get_value(post, ('images', 0, 'id', ))
            size = self.get_value(post, ('mp4_size', ))
            if size is None:
                size = self.get_value(post, ('images', 0, 'mp4_size', ))
            if media is None:
                media = self.get_value(post, ('mp4', ))
        else:
            self.logger.log(logger.LogLevel.WARNING, 'mediaType is not Image or Video')
            return None

        #check if image/video is over max size
        if mediaType == MediaType.IMAGE:
            if size >= self.setting.maxImageSize:
                return None
        elif mediaType == MediaType.VIDEO:
            if size >= self.setting.maxVideoSize:
                return None

        postId = self.get_value(post, ("id", ))
        title = self.get_value(post, ("title", ))
        views = self.get_value(post, ("views", ))
        ups = self.get_value(post, ("ups", ))
        downs = self.get_value(post, ("downs", ))
        return Post(postId, title, mediaType.value, media, size, tag, views, ups, downs)
    
    def post_to_tuple(self, tweetId, post):
        """ Takes post and returns as tuple """
        return (tweetId, post.postId, post.title, post.mediaType, post.media, post.size, post.views, post.ups, post.downs, post.tag)

    def print_post(self, tag):
        req = requests.get('%s%s' % (self.setting.tagLink, tag), headers=self.setting.imgurHeaders)
        for post in req.json()['data']['items']:
            print(post)
    
    def get_rates(self):
        req = requests.get('https://api.imgur.com/3/credits', headers=self.setting.imgurHeaders)
        print('X-RateLimite-UserLimit: %s' % str(req.headers.get('X-RateLimit-UserLimit')))
        print('X-RateLimit-UserRemaining: %s' % str(req.headers.get('X-RateLimit-UserRemaining')))
        print('X-RateLimit-UserReset: %s' % str(req.headers.get('X-RateLimit-UserReset')))
        print('X-RateLimit-ClientLimit: %s' % str(req.headers.get('X-RateLimit-ClientLimit')))
        print('X-RateLimit-ClientRemaining: %s' % str(req.headers.get('X-RateLimit-ClientRemaining')))