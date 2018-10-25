import os
import random
import requests
import datetime
import time
import util.logger as logger
import twitter.twitter as twitter
import imgur.imgur as imgur
import database.database as database
import debug.debug as debug
import database.query as query
import util.settings as settings

class TweetThread():
    def __init__(self, log, setting, db, twit, imgr):
        self.log = log
        self.setting = setting
        self.db = db
        self.twit = twit
        self.imgr = imgr

    def run(self):
        self.log.log(logger.LogLevel.INFO, 'tweet_thread.run() is now running: %s' % self.setting.runTweetThread)
        while self.setting.runTweetThread:
            secDelay = self.delay_tweet()
            self.log.log(logger.LogLevel.INFO, 'Tweeting in %d seconds' % secDelay)
            time.sleep(secDelay)

            # Tweet an image
            tweeted = False
            postList = self.imgr.get_posts()
            postList.sort(key=lambda x: x.views, reverse=True)
            for post in postList:
                self.log.log(logger.LogLevel.DEBUG, 'Trying to tweet(%s): %s' % (post.mediaType, post.postId))
                if self.tweeted_before(self.db, post) is False:
                    tweeted = self.tweet(post)
                    if tweeted is False:
                        self.log.log(logger.LogLevel.DEBUG, 'Post that failed to tweet | mediaType: %s, size: %s' % (post.mediaType, str(post.size)))
                        continue
                    else:
                        self.add_tweet_db(post, tweeted)
                        break
                else:
                    self.log.log(logger.LogLevel.DEBUG, 'Already tweeted(%s): %s' % (post.mediaType, post.postId))
            if tweeted is False:
                self.log.log(logger.LogLevel.CRITICAL, 'Failed to tweet | len(postList): %d' % len(postList))
            
            # Updates tweet's statistics
            endDate = datetime.datetime.now() - self.setting.updateTweetAfter
            tweetUpdateList = self.db.query_fetchall(query.QUERY_GET_TWEET_UPDATE_QUEUE(), (endDate, ))
            for tweet in tweetUpdateList:
                try:
                    tweetId = tweet[0]
                    favorites, retweets = self.twit.get_tweet_stats(tweetId)
                    # If tweet has been deleted/ no connection to twitter API
                    if favorites is False:
                        dbCommit = self.db.query_commit(query.QUERY_UPDATE_TWEET_DELETED(), (tweetId, ))
                        if dbCommit:
                            self.log.log(logger.LogLevel.INFO, 'Tweet: %s, has been deleted. Updated database successfully' % tweetId)
                        else:
                            self.log.log(logger.LogLevel.ERROR, 'Tweet: %s, has been deleted. Failed to update database' % tweetId)
                        continue
                    elif favorites is None:
                        self.log.log(logger.LogLevel.WARNING, 'Failed to get tweet stats for tweetId: %s' % tweetId)
                        continue
                    
                    updated = self.db.query_commit(query.QUERY_UPDATE_POSTS(), (favorites, retweets, tweetId))
                    if updated:
                        self.log.log(logger.LogLevel.INFO, 'Updated statistics for tweet id: %s' % tweetId)
                    else:
                        self.log.log(logger.LogLevel.WARNING, 'Failed to update statistics for tweet id: %s, favorites: %s, retweets: %s' % (tweetId, favorites, retweets))
                except Exception as e:
                        self.log.log(logger.LogLevel.ERROR, 'Failed to update statistics for tweet id: %s | %s' % (tweetId, e))
        
        self.log.log(logger.LogLevel.CRITICAL, 'tweet_thread.run is not running anymore: %s' % self.setting.runTweetThread)

    def tweet(self, post):
        """ Tweets an image. Returns twitter post id if successfull, False otherwise """
        hashTags = self.get_hashtags(self.setting.hashTags)

        if post.mediaType == imgur.MediaType.IMAGE.value:
            media = self.download_image(self.log, post.media)
            if media is None:
                self.log.log(logger.LogLevel.WARNING, 'post.mediaType: %s. Unable to download_image' % post.media)
                return False
            return self.twit.tweet_image('%s %s' % (post.title, hashTags), media)
        else:
            media = self.download_video(self.log, post.media)
            if media is None:
                self.log.log(logger.LogLevel.WARNING, 'post.mediaType: %s. Unable to download_video' % post.media)
                return False
            return self.twit.tweet_video('%s %s' % (post.title, hashTags), media)
        return False

    def get_hashtags(self, hashTags):
        """ Gets a random amount of hashtags between 1 and 5(or highest amount of hashTags available) """
        max = 5
        if max > len(hashTags):
            max = len(hashTags)
        amount = random.randint(1, max)
        return ' '.join(random.sample(hashTags, amount))

    def add_tweet_db(self, post, tweetId):
        dbPosts = self.db.query_commit(query.QUERY_INSERT_POSTS(), self.imgr.post_to_tuple(tweetId, post))
        dbTweets = self.db.query_commit(query.QUERY_INSERT_TWEETS(), (tweetId, datetime.datetime.now()))
        if dbPosts and dbTweets:
            self.log.log(logger.LogLevel.INFO, 'Added tweet: %s to database' % post.postId)
        else:
            self.log.log(logger.LogLevel.ERROR, 'Added tweet to table \'%s\': %s' % (query.TABLE_TWEETS, dbTweets))
            self.log.log(logger.LogLevel.ERROR, 'Added tweet to table \'%s\': %s' % (query.TABLE_POSTS, dbPosts))

    def download_image(self, log, imageID):
        """ Downloads image """
        fileName = '%s.jpg' % self.setting.tempFile
        url = '%s%s.jpg' % (self.setting.downloadBaseurl, imageID)
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(fileName, 'wb') as image:
                for chunk in r:
                    image.write(chunk)
            return fileName
        else:
            if os.path.isfile(fileName):
                os.remove(fileName)
            self.log.log(logger.LogLevel.ERROR, 'Failed to download image: %s' % url)
            return None

    def download_video(self, log, videoID):
        """ Downloads video (mp4) """
        fileName = '%s.mp4' % self.setting.tempFile
        url = '%s%s.mp4' % (self.setting.downloadBaseurl, videoID)
        try:
            with open(fileName, 'wb') as file:
                response = requests.get(url)
                file.write(response.content)
            return fileName
        except Exception as e:
            if os.path.isfile(fileName):
                os.remove(fileName)
            self.log.log(logger.LogLevel.ERROR, 'Failed to download video: %s | %s' % (url, e))
            return None

    def tweeted_before(self, db, post):
        return self.db.query_exists(query.QUERY_ALREADY_TWEETED(), (post.postId, post.media))

    def delay_update_tweet(self, tweetDate):
        """ Returns amount of seconds till tweet should be updated (24hours after tweetDate) """
        time = datetime.datetime.strptime(tweetDate, '%Y-%m-%d %H:%M:%S.%f') + self.setting.updateTweetAfter
        return (time - datetime.datetime.now()).seconds

    def delay_tweet(self):
        """ Returns how many seconds left to whole hour | xx:00 """
        minutes = 59 - int(time.strftime("%M"))
        seconds = 60 - int(time.strftime("%S"))
        return (minutes * 60) + seconds