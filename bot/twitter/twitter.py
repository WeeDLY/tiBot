from TwitterAPI import TwitterAPI
import sys
import os
sys.path.append("..")
import util.logger as logger
import util.settings as settings

class Twitter():
    """ Twitter class """
    def __init__(self, logger, setting):
        self.authenticated = False
        self.api = None
        self.log = logger
        self.setting = setting
    
    def authenticate(self):
        """ Authenticates user to Twitter API """
        self.api = TwitterAPI(self.setting.consumerKey, self.setting.consumerSecret,
                                self.setting.accessToken, self.setting.accessSecret)
        r = self.api.request('account/verify_credentials')
        if r.status_code == 200:
            if r.json()['screen_name'] == self.setting.twitterName:
                self.authenticated = True
                self.log.log(logger.LogLevel.INFO, 'Twitter authenticated successfully')
            else:
                self.log.log(logger.LogLevel.WARNING, 'Twitter authenticated on wrong user!')
        else:
            self.log.log(logger.LogLevel.ERROR, 'Twitter failed to authenticate. Response: %s | %s' % (r.status_code, r.text))
    
    def get_user_search(self, screen_name):
        r = self.api.request('users/show', {'screen_name':screen_name})
        if r.status_code == 200:
            self.log.log(logger.LogLevel.DEBUG, 'Twitter user: %s exists' % screen_name)
            return True
        else:
            self.log.log(logger.LogLevel.WARNING, 'Twitter user: %s does not exist' % screen_name)
            return False

    def get_user_stats(self):
        """ returns followers, tweets, friends, favorites to the authenticated user """ 
        r = self.api.request('account/verify_credentials')
        if r.status_code == 200:
            self.log.log(logger.LogLevel.DEBUG, 'twitter.get_user_stats: Got user statistics.')
            return r.json()['followers_count'], r.json()['statuses_count'], r.json()['friends_count'], r.json()['favourites_count']
        else:
            self.log.log(logger.LogLevel.ERROR, 'twitter.get_user_stats: Failed to get user stats')
            return None
    
    def delete_tweet(self, tweetId):
        """ Deletes a tweet based on tweetId """
        r = self.api.request('statuses/destroy/:%s' % tweetId)
        if r.status_code == 200:
            self.log.log(logger.LogLevel.INFO, 'Deleted tweet: %s' % tweetId)
            return True
        else:
            self.log.log(logger.LogLevel.WARNING, 'Unable to delete tweet: %s' % tweetId)
            return False

    def delete_last_tweets(self, amount):
        """ Deletes last <amount> tweets of user """
        r = self.api.request('statuses/user_timeline', {'count':amount})
        deletedTweets = 0
        for tweet in r:
            if 'id' in tweet:
                tweetId = tweet['id']
                deleted = self.delete_tweet(tweetId)
                if deleted:
                    deletedTweets += 1
        self.log.log(logger.LogLevel.INFO, 'Deleted: %d/%d last tweets' % (deletedTweets, amount))

    def get_tweet_stats(self, tweetId):
        """ Returns favorites, retweets of tweetId. If returns False, tweet has been deleted.
            If None, something went wrong(for example: no internet connection) """
        r = self.api.request('statuses/show/:%s' % tweetId)
        if r.status_code == 200:
            favorites = r.json()['favorite_count']
            retweets = r.json()['retweet_count']
            return favorites, retweets
        # Tweet has most likely been deleted
        elif r.status_code == 404:
            c = r.json()['errors'][0]
            code = c['code']
            if code == 144:
                self.log.log(logger.LogLevel.INFO, 'Tweet: %s has been deleted' % tweetId)
                return False, False
            self.log.log(logger.LogLevel.ERROR, 'twitter.get_tweet_stats: status_code: %d | %s' % (r.status_code, r.text))
            return None, None
        else:
            self.log.log(logger.LogLevel.WARNING, 'Unable to get statistics for tweet: %s' % tweetId)
            return None, None

    def tweet_text(self, msg):
        """ Tweets with only text """
        r = self.api.request('statuses/update', {'status':msg})
        if r.status_code == 200:
            self.log.log(logger.LogLevel.INFO, 'Tweeted(text): %s' % msg)
            return True
        else:
            self.log.log(logger.LogLevel.ERROR, 'Failed to tweet(text): %s' % msg)
            return False
    
    def tweet_image(self, msg, img):
        """ Tweets with text + image | returns tweetId, or False"""
        uImg = self.upload_image(img)
        if uImg is None:
            return False

        r = self.api.request('statuses/update', {'status': msg, 'media_ids': uImg})
        if r.status_code == 200:
            self.log.log(logger.LogLevel.INFO, 'Tweeted(img): %s | %s' % (msg, img))
            return r.json()['id']
        else:
            self.log.log(logger.LogLevel.ERROR, 'Failed to tweet(img): %s, %s | %s' % (msg, img, r.text))
            return False

    def upload_image(self, img):
        """ Uploads image to twitter's server. This is needed to be able to tweet that image """
        data = open(img, 'rb').read()
        r = self.api.request('media/upload', None, {'media':data})
        mediaId = r.json()['media_id']
        if r.status_code == 200:
            self.log.log(logger.LogLevel.INFO, 'Succesfully uploaded image: %s' % mediaId)
            return mediaId
        else:        
            self.log.log(logger.LogLevel.ERROR, 'Failed to upload image: %s' % img)
            return None

    def tweet_video(self, msg, vid):
        """ Tweets text video(mp4). Returns tweetId, or False """
        uVid = self.upload_video(vid)
        if uVid is None:
            self.log.log(logger.LogLevel.WARNING, 'uVid is None. msg: %s, %s' % (msg, vid))
            return False

        r = self.api.request('statuses/update', {'status':msg, 'media_ids':uVid})
        if r.status_code == 200:
            self.log.log(logger.LogLevel.INFO, 'Tweeted(vid): %s | %s' % (msg, uVid))
            return r.json()['id']
        else:
            self.log.log(logger.LogLevel.ERROR, 'Failed to tweet(vid): %s | %s\nStatus code: %d: %s' % (msg, uVid, r.status_code, r.json()))
            return False

    def upload_video(self, vid):
        """ Uploads video(mp4) to Twitter's server. This is needed to be able to tweet that video """
        totalBytes = os.path.getsize(vid)
        try:
            upload = self.api.request('media/upload', {'command':'INIT', 'media_type':'video/mp4', 'total_bytes':totalBytes})
            mediaId = upload.json()['media_id']
        except Exception as e:
            self.log.log(logger.LogLevel.ERROR, 'Uploading INIT: %s' % e)
            return None

        file = open(vid, 'rb')
        segmentId = 0
        bytesSent = 0
        while bytesSent < totalBytes:
            chunk = file.read(4*1024*1024)
            try:
                r = self.api.request('media/upload', {'command':'APPEND', 'media_id':mediaId, 'segment_index':segmentId}, {'media':chunk})
                if self.check_upload_video_status(r, mediaId) is False:
                    return None
            except Exception as e:
                self.log.log(logger.LogLevel.ERROR, 'Uploading APPEND(%d): %s as %s | BytesSent: %d/%d\nException: %s' % (segmentId, mediaId, vid, bytesSent, totalBytes, e))
                return None
            segmentId += 1
            bytesSent += file.tell()
            self.log.log(logger.LogLevel.DEBUG, 'Uploading(%d): %s as %s | BytesSent: %d/%d' % (segmentId, mediaId, vid, bytesSent, totalBytes))
        try:
            r = self.api.request('media/upload', {'command':'FINALIZE', 'media_id':mediaId})
        except Exception as e:
            self.log.log(logger.LogLevel.ERROR, 'Uploading FINALIZE: %s as %s\nException %s' % (mediaId, vid, e))
            return None

        if self.check_upload_video_status(r, mediaId) is False:
            return None
        else:
            self.log.log(logger.LogLevel.INFO, 'Uploaded video successfully: %s' % mediaId)
            return mediaId

    def check_upload_video_status(self, r, mediaId):
        """ Checks the status of uploading a video """
        if r.status_code < 200 or r.status_code > 299:
            self.log.log(logger.LogLevel.ERROR, 'Failed to upload video: %s\n%d: %s' % (mediaId, r.status_code, r.text))
            return False
        else:
            return True

    def retweet(self, tweetId):
        """ Retweets a tweet, by tweetId. Return boolean """
        r = self.api.request('statuses/retweet/:%s' % tweetId)
        if r.status_code == 200:
            self.log.log(logger.LogLevel.INFO, 'Retweeted: %s' % tweetId)
            return True
        else:
            self.log.log(logger.LogLevel.WARNING, 'Could not retweet: %s' % tweetId)
            return False

    def follow_by_id(self, followId):
        """ Follows a person, by user_id """
        r = self.api.request('friendships/create', {'user_id':followId})
        screenName = r.json()['screen_name']
        if r.status_code == 200:
            self.log.log(logger.LogLevel.INFO, 'Followed: %s, (%s)' % (screenName, followId))
            return True
        else:
            self.log.log(logger.LogLevel.WARNING, 'twitter.follow_by_id(): Unable to follow: %s' % followId)
            return False

    def unfollow_by_id(self, followId):
        """ Unfollows a person based on user_id """
        r = self.api.request('friendships/destroy', {'user_id': followId})
        screenName = r.json()['screen_name']
        if r.status_code == 200:
            self.log.log(logger.LogLevel.INFO, "Unfollowed: %s (%s)" % (screenName, followId))
            return True
        else:
            self.log.log(logger.LogLevel.WARNING, "Failed to unfollow: %s" % followId)
            return False
    
    def follow_by_name(self, screenName):
        """ Follows a person based on screen_name """
        r = self.api.request('friendships/create', {'screen_name':screenName})
        if r.status_code == 200:
            self.log.log(logger.LogLevel.INFO, 'Followed: %s' % screenName)
            return True
        else:
            self.log.log(logger.LogLevel.WARNING, 'twitter.follow_by_name: Unable to follow: %s' % screenName)
            return False
    
    def unfollow_by_name(self, screenName):
        """ Unfollows a person based on user_id """
        try:
            r = self.api.request('friendships/destroy', {'screen_name': screenName})
            if r.status_code == 200:
                self.log.log(logger.LogLevel.INFO, "Unfollowed: %s" % screenName)
                return True
            else:
                self.log.log(logger.LogLevel.WARNING, "Failed to unfollow: %s" % followId)
                return False
        except Exception as e:
                self.log.log(logger.LogLevel.ERROR, "Failed to unfollow, with exception: %s" % e)
                return False
    
    def get_rates(self):
        """ Only used for debugging, not relevant to log"""
        r = self.api.request('application/rate_limit_status')
        print(r.text)
        print(r.headers)

    def search(self, q, count):
        try:
            r = self.api.request('search/tweets', {'q':q, 'count': count})
            if r.status_code == 200:
                return r
        except Exception as e:
            self.log.log(logger.LogLevel.ERROR, "twitter.search(%s): %s" % (q, e))
            return None