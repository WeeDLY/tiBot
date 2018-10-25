import datetime
import util.logger as logger
import json
import os

class Settings():
    def __init__(self, settingsFile):
        self.settingsFile = settingsFile
        self.runBot = True
        self.maxImageSize = 5000000 # Max image size twitter supports.
        self.maxVideoSize = 15000000 # Max video size twitter supports.
        self.authLink = "https://api.imgur.com/3/gallery/r/a" # Imgur link used to check authentication
        self.tagLink = "https://api.imgur.com/3/gallery/t/" # Imgur base link for searching up tags
        self.postBaseurl = "https://imgur.com/gallery/" # Imgur base link for searching up a post
        self.downloadBaseurl = "https://i.imgur.com/" # Imgur base link for downloading a post

        if os.path.isfile(self.settingsFile) is False:
            print('%s does not exist. Exiting' % self.settingsFile)
            exit()
        try:
            settingsData = open(self.settingsFile)
            data = json.load(settingsData)
            self.runTweetThread = data["overall"]["runTweetThread"]
            self.runFollowThread = data["overall"]["runFollowThread"]
            self.database = data["overall"]["database"]
            self.backupFolder = data["overall"]["backupDatabase"]

            self.logFileName = data["logger"]["logFileName"]
            self.LOGGER_PRINT_LEVEL = self.get_logger_print_level(data["logger"]["lOGGER_PRINT_LEVEL"])
            self.logFolder = data["logger"]["logFolder"]
            self.logSize = data["logger"]["logSize"]

            self.consumerKey = data["twitter"]["consumerKey"]
            self.consumerSecret = data["twitter"]["consumerSecret"]
            self.accessToken = data["twitter"]["accessToken"]
            self.accessSecret = data["twitter"]["accessSecret"]
            self.twitterName = data["twitter"]["twitterName"]
            self.tempFile = "resources/%s" % data["twitter"]["tempFile"]
            self.hashTags = data["twitter"]["hashTags"]
            self.followTweetsMin, self.followTweetsMax = self.read_2values_array(data["twitter"]["followTweets"])
            self.followFriendsMin, self.followFriendsMax = self.read_2values_array(data["twitter"]["followFriends"])
            self.followFollowersMin, self.followFollowersMax = self.read_2values_array(data["twitter"]["followFollowers"])
            self.followFavoritesMin, self.followFavoritesMax = self.read_2values_array(data["twitter"]["followFavorites"])
            
            self.updateStatHour = data["twitter"]["updateStatHour"]
            self.updateTweetAfter = self.read_datetime_array(data["twitter"]["updateTweetAfter"])
            self.followNewPerson = self.read_datetime_array(data["twitter"]["followNewPerson"])
            self.unfollowPersonAfter = self.read_datetime_array(data["twitter"]["unfollowPersonAfter"])

            self.imgurHeaders = {'authorization':'Client-Id %s' % data["imgur"]["clientId"]}
            self.imgurTags = data["imgur"]["tags"]
        except Exception as e:
            print('Exception: %s' % e)

    def check_all_settings(self):
        if type(self.updateTweetAfter) != datetime.timedelta:
            return False
        if type(self.followNewPerson) != datetime.timedelta:
            return False
        if type(self.unfollowPersonAfter) != datetime.timedelta:
            return False
        if type(self.followTweetsMin) != int:
            return False
        if type(self.followTweetsMax) != int:
            return False
        if type(self.followFriendsMin) != int:
            return False
        if type(self.followFriendsMax) != int:
            return False
        if type(self.followFollowersMin) != int:
            return False
        if type(self.followFollowersMax) != int:
            return False
        if type(self.followFavoritesMin) != int:
            return False
        if type(self.followFavoritesMax) != int:
            return False
        return True

    def get_logger_print_level(self, printLevel):
        if printLevel == "debug":
            return logger.LogLevel.DEBUG
        elif printLevel == "info":
            return logger.LogLevel.INFO
        elif printLevel == "warning":
            return logger.LogLevel.WARNING
        elif printLevel == "error":
            return logger.LogLevel.ERROR
        elif printLevel == "critical":
            return logger.LogLevel.CRITICAL
        else:
            return logger.LogLevel.DEBUG

    def read_2values_array(self, arr):
        try:
            return arr[0], arr[1]
        except:
            return None, None

    def read_datetime_array(self, arr):
        try:
            return datetime.timedelta(days=arr[0], hours=arr[1])
        except:
            return None, None