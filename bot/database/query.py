TABLE_STATS = 'stats'
TABLE_TWEETS = 'tweets'
TABLE_POSTS = 'posts'
TABLE_FOLLOWS = 'follows'

def QUERY_UPDATE_FOLLOWS():
    """ Query that updates favorites/retweets on a tweet, based on tweetId """
    return """UPDATE %s SET followingNow = 0 WHERE screenName = ? """ % TABLE_FOLLOWS

def QUERY_GET_FOLLOWS_UPDATE_QUEUE():
    """ Query that returns everyone who you followed more than setting.unfollowPersonAfter ago """
    return """SELECT * FROM %s where followDate <= ? AND followingNow = 1 """ % TABLE_FOLLOWS

def QUERY_GET_FOLLOWS():
    """ Query that selects * from TABLE_FOLLOWS, based on screenName """
    return """SELECT *  FROM %s WHERE screenName = ? """ % TABLE_FOLLOWS

def QUERY_INSERT_FOLLOWS():
    """ Query that inserts a user, I've followed to TABLE_FOLLOWS """
    return """INSERT INTO %s VALUES (?, ?, ?) """ % TABLE_FOLLOWS

def QUERY_INSERT_STATS():
    """ Query that inserts user stats to TABLE_STATS """
    return """INSERT INTO %s VALUES(?, ?, ?, ?, ?)""" % TABLE_STATS

def QUERY_ALREADY_TWEETED():
    """ Query that checks if a post has already been tweeted """
    return """SELECT * FROM %s WHERE postId = ? OR media = ? """ % TABLE_POSTS

def QUERY_UPDATE_TWEET_DELETED():
    """ Query that updates a tweet, that has been deleted """
    return """UPDATE %s SET tweetExists = 0 WHERE tweetId = ? """ % TABLE_TWEETS

def QUERY_GET_TWEET_UPDATE_QUEUE():
    """ Query that returns tweets older than setting.updateTweetAfter.
        That has not yet been updated. Limit 100, because we don't want to overreach twitter's rate limit """
    return """SELECT * FROM %s WHERE tweetDate <= ? AND updated = 0 AND tweetExists = 1 ORDER BY tweetDate ASC LIMIT 100""" % TABLE_TWEETS

def QUERY_UPDATE_POSTS():
    """ Query that updates favorites/retweets on a tweet, based on tweetId """
    return """UPDATE %s SET favorites = ?, retweets = ?, updated = 1 WHERE tweetId = ? """ % TABLE_TWEETS

def QUERY_GET_POSTS():
    """ Query that selects * from TABLE_POSTS, based on tweetId """
    return """SELECT * FROM %s WHERE tweetId = ? """ % TABLE_TWEETS

def QUERY_INSERT_TWEETS():
    """ Query that inserts a tweet, into table: TABLE_TWEETS """
    return """INSERT INTO %s VALUES(?, ?, 0, 0, 0, 1)""" % TABLE_TWEETS

def QUERY_INSERT_POSTS():
    """ Query that inserts a Imgur.Post, into table: TABLE_POSTS """
    return """INSERT INTO %s VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""" % TABLE_POSTS

def QUERY_TABLE_EXISTS():
    """ Query that checks if a table exists in the database """
    return "SELECT name FROM sqlite_master WHERE type='table' AND name=?"

def QUERY_CREATE_TABLE_FOLLOWS():
    """ Create query for TABLE_FOLLOWS """
    return """
        CREATE TABLE %s(
            screenName text PRIMARY KEY,
            followDate date,
            followingNow boolean
        )""" % TABLE_FOLLOWS

def QUERY_CREATE_TABLE_STATS():
    """ Create query for TABLE_TWEETS """
    return """
        CREATE TABLE %s(
            lastUpdate date PRIMARY KEY,
            followers int,
            tweets int,
            friends int,
            favorites int
            )""" % TABLE_STATS

def QUERY_CREATE_TABLE_TWEETS():
    """ Create query for TABLE_TWEETS """
    return """
        CREATE TABLE %s(
            tweetId text PRIMARY KEY,
            tweetDate date,
            favorites int,
            retweets int,
            updated boolean,
            tweetExists boolean
            )""" % TABLE_TWEETS

def QUERY_CREATE_TABLE_POSTS():
    """ Create query for TABLE_POSTS """
    return """
        CREATE TABLE %s(
            tweetId text,
            postId text PRIMARY KEY,
            title text,
            mediaType text,
            media text,
            size int,
            views int,
            ups int,
            downs int,
            tag text,
            FOREIGN KEY(tweetId) REFERENCES %s(tweetId)
            )""" % (TABLE_POSTS, TABLE_TWEETS)