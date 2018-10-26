# This is a twitter/imgur bot.
Bot is written entirely in Python3.
This bot is a twitter/imgur bot.
Bot is the actualy bot itself.
Server is a python flask server that displays information about the bot.
Server does not affect the actual bot itself at all.

## Bot
The bot will take posts from imgur and tweet them.
All posts and tweets are stored in a database.
It support all different tweet formats.

It can also follow and unfollow people based on preferences you can set.

Every day at 00:00 it will update overall twitter stats and take backup of database, if configured to do so.

Everything from posts, statistics will be stored in a sqlite database.

Everything the bot does, will be logged.

### Settings.json
    overall:
        runTweetThread: true/false disabling the bot tweeting
        runFollowThread: true/false disabling the bot following/unfollowing people
        database: location for the database
        backupDatabase: folder in which the database backups are stored. Takes backup everyday at midnight. Does not take backup if folder is empty.
    logger:
        logFileName: name for the log files, do not include extension.
        lOGGER_PRINT_LEVEL: Level that is printed to console(everything is logged). Options are: debug, info, warning, error, critical.
        logFolder: Folder for the log files
        logSize: Max size of a single log file.
    twitter:
        consumerKey: twitter consumer key
        consumerSecret: twitter consumer secret
        accessToken: twitter access token
        accessSecret: twitter access secret
        twitterName: twitter name
        tempFile: temporary file to store images/mp4 before it gets uploaded to twitter. Do not include extension.
        hashTags: Array of hash tags. It will randomize hashtags based on this array.
        Criterias for you to follow a person. All are arrays with 2 values (min, max)
            followTweets: Amount of tweets the person has to have.
            followFriends: Amount of people the person is following.
            followFollowers: Amount of followers the person has.
            followFavorites: Amounf of likes the person has.
        updateStatHour: The time of hour when stats are updated
        updateTweetAfter: Array with 2 values. Days and hours. Amount of time, untill a statistics of a tweet is updated.
        followNewPerson: How often a new person is followed. Array with 2 values, days and hours.
        unfollowPersonAfter: How long time after following a person, you unfollow them. Array with 2 values, days and hours.

## Server
Python flask server.
Website with statistics about the state of the bot.

### Overall
General information, such as:

1. Current time
2. Twitter name
3. Runtime
4. Last tweet
5. + General twitter statistics etc..

### Settings.json
    twitterName: Name of your twitter user
    database: Location of your bot's database
    logFolder: Folder location of your bot's log folder

### Query
Can query the database directly and fetch the result.
Will NOT commit the queries.

### Debug
Able to read the log files the bot produces from the website

### About
General information