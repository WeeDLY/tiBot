import sqlite3
import sys
import datetime
sys.path.append("..")
import argparse
import database.query as query
import util.logger as logger
import util.settings as settings
import twitter.twitter as twitter
import imgur.imgur as imgur
import database.database as database
import requests

debugMode = True

def debug(log, setting, db, twit, imgr):
    global debugMode
    print('Debug mode started')
    debug_commands()
    while debugMode:
        cmd = input('$ ')
        cmd = cmd.lower()
        if cmd == 'database':
            database_mode(log, setting, db)
        elif cmd == 'twitter':
            twitter_mode(log, db, twit)
        elif cmd == 'imgur':
            imgur_mode(log, setting, imgr)
        elif cmd == 'e' or cmd == 'q':
            debugMode = False

def imgur_mode(log, setting, imgr):
    debugImgur = True
    while debugImgur:
        cmd = input('imgur $ ')
        cmd = cmd.lower()
        if cmd == 'e':
            debugImgur = False
        elif cmd == 'test tag':
            imgr.print_post('meme')
        elif cmd == 'test post':
            post = input('postID: ')
            r = requests.get('https://api.imgur.com/3/image/%s' % post, headers=setting.imgurHeaders)
            print(r.text)
        elif cmd =='download':
            id = input('id: ')
            url = 'https://i.imgur.com/%s.mp4' % id
            fileName = "resources/debug.mp4"
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(fileName, 'wb') as image:
                    for chunk in r:
                        image.write(chunk)
                return fileName
            else:
                print('Can\'t download image: %s id')
        elif cmd == 'get rates':
            imgr.get_rates()


def twitter_mode(log, db, twit):
    debugTwitter = True
    while debugTwitter:
        cmd = input('twitter $ ')
        cmd = cmd.lower()
        if cmd == 'e':
            debugTwitter = False
        elif cmd == 'test tweet':
            testPost = imgur.Post('1Gyav', 'Online gaming in a nutshell', imgur.MediaType.IMAGE, 'https://i.imgur.com/LLqrC7R.jpg', 1000, 'aww', 0, 0, 0)
            twit.tweet_image(testPost.title, 'resources/test.jpg')
        elif cmd == 'rate limit':
            rates = twit.get_rate_limit()
            print(rates)
        elif cmd == 'get suggested':
            personList = twit.get_suggested("#meme", 10)
            for person in personList:
                print(person)
        elif cmd == 'unfollow person':
            screenName = input('screen name: ')
            resp = twit.unfollow_person(screenName)
            print('Unfollowed: %s | %s' % (screenName, resp))
        elif cmd == 'test tweet gif':
            testPost = imgur.Post('1Gyav', 'Online gaming in a nutshell', imgur.MediaType.VIDEO, 'https://i.imgur.com/BpklzcF.mp4', 1000, 'aww', 0, 0, 0)
            twit.tweet_video(testPost.title, 'resources/test.mp4')
            print('done')
        elif cmd == 'get rates':
            twit.get_rates()
        elif cmd == 'check person':
            person = input('person: ')
            twit.get_user_search(person)
        elif cmd == 'delete last tweets':
            try:
                num = int(input('amount: '))
                twit.delete_last_tweets(num)
            except Exception as e:
                print(e)
        elif cmd == 'search twitter':
            try:
                search = input('q: ')
                twit.search(search, 15)
            except Exception as e:
                print(e)
        elif cmd == 'get tweet stats':
            favorites, retweets = twit.get_tweet_stats('971765181230481409')
            print(favorites)
            print(retweets)
            

def database_mode(log, setting, db):
    debugDatabase = True
    while debugDatabase:
        cmd = input('database $ ')
        cmd = cmd.lower()
        if cmd == 'print database':
            db.database_dump()
        elif cmd == 'print stats':
            db.database_table_dump(query.TABLE_STATS)
        elif cmd == 'print tweets':
            db.database_table_dump(query.TABLE_TWEETS)
        elif cmd == 'print posts':
            db.database_table_dump(query.TABLE_POSTS)
        elif cmd == 'print follows':
            db.database_table_dump(query.TABLE_FOLLOWS)
        elif cmd == 'e':
            debugDatabase = False
        elif cmd == 'print tweets update':
            endDate = datetime.datetime.now() - setting.updateTweetAfter
            tweetList = db.query_fetchall(query.QUERY_GET_TWEET_UPDATE_QUEUE(), (endDate, ))
            for tweet in tweetList:
                print(tweet)
        elif cmd == 'print unfollow list':
            endDate = datetime.datetime.now() - setting.unfollowPersonAfter
            personList = db.query_fetchall(query.QUERY_GET_FOLLOWS_UPDATE_QUEUE(), (endDate, ))
            for person in personList:
                print(person)
        elif cmd == 'query':
            queryMode = True
            while queryMode:
                q = input('database : query $ ')
                if q == 'e':
                    queryMode = False
                    break
                elif q == 'commit':
                    query = input('database : query-commit $ ')
                    res = db.query_commit(query)
                    print(res)
                else:
                    results = db.query_fetchall(q)
                    for result in results:
                        print(result)
                

def debug_commands():
    print('=====COMMAND LIST=====')
    print('database')
    print('twitter')
    print('imgur')
    print('\'e\' or \'q\' to quit')
    print()