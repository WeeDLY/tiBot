import random
import time
import datetime
import util.logger as logger
import twitter.twitter as twitter
import imgur.imgur as imgur
import database.database as database
import database.query as query
import util.settings as settings

class TwitterAccount():
    def __init__(self, screenName, followers, friends, favorites, tweets):
        self.screenName = screenName
        self.followers = followers
        self.friends = friends
        self.favorites = favorites
        self.tweets = tweets

    def to_string(self):
        return '%s: %d %d %d %d' % (self.screenName, self.followers, self.friends, self.favorites, self.tweets)

def run(log, setting, db, twit, imgr):
    log.log(logger.LogLevel.INFO, 'follow_thread.run is now running: %s' % setting.runFollowThread)
    while setting.runFollowThread:
        # Find a person
        q = get_search_q(setting)
        result = twit.search(q, 100)
        person = None
        if result is None:
            log.log(logger.LogLevel.WARNING, 'follow_thread.run: No result when searching \'%s\'' % q)
        else:
            personList = get_person_list(result)
            person = get_person(db, personList, setting)

        # Follow person
        if person is None:
            log.log(logger.LogLevel.WARNING, 'Did not find anyone to follow out of: %d' % len(personList))
        else:
            followed = twit.follow_by_name(person.screenName)
            if followed:
                q = db.query_commit(query.QUERY_INSERT_FOLLOWS(), (person.screenName, datetime.datetime.now(), 1))
                if q:
                    log.log(logger.LogLevel.DEBUG, 'Added %s to database' % person.screenName)
                else:
                    log.log(logger.LogLevel.ERROR, 'Failed to add %s to database' % person.screenName)
            else:
                log.log(logger.LogLevel.WARNING, 'Failed to follow: %s' % person.to_string())
        
        # Unfollow person
        endDate = datetime.datetime.now() - setting.unfollowPersonAfter
        personList = db.query_fetchall(query.QUERY_GET_FOLLOWS_UPDATE_QUEUE(), (endDate, ))
        for person in personList:
            screenName = person[0]
            unfollowed = twit.unfollow_by_name(screenName)
            if unfollowed:
                unfollow_in_db(log, db, screenName)
            else:
                res = twit.get_user_search(screenName)
                if res is False:
                    unfollow_in_db(log, db, screenName)
                else:
                    log.log(logger.LogLevel.ERROR, 'Failed to unfollow a person that exists: %s' % screenName)

        log.log(logger.LogLevel.INFO, 'follow_thread.run() sleeping for: %d' % setting.followNewPerson.total_seconds())
        time.sleep(setting.followNewPerson.total_seconds())
    log.log(logger.LogLevel.CRITICAL, 'follow_thread.run is not running anymore: %s' % self.setting.runFollowThread)

def unfollow_in_db(log, db, screenName):
    dbResult = db.query_commit(query.QUERY_UPDATE_FOLLOWS(), (screenName, ))
    if dbResult:
        log.log(logger.LogLevel.DEBUG, 'Updated database: %s unfollowed successfully' % screenName)
    else:
        log.log(logger.LogLevel.ERROR, 'Unable to update followingNow status on person: %s' % screenName)

def get_person(db, personList, setting):
    for person in personList:
        if db.query_exists(query.QUERY_GET_FOLLOWS(), (person.screenName, )):
            continue
        
        validStats = person_valid_stats(person, setting)
        if validStats:
            return person
    return None

def person_valid_stats(ta, setting):
    """ checks if the person fits statistics criteria """
    if ta.tweets < setting.followTweetsMin or ta.tweets > setting.followTweetsMax:
        return False
    if ta.friends < setting.followFriendsMin or ta.friends > setting.followFriendsMax:
        return False
    if ta.followers < setting.followFollowersMin or ta.followers > setting.followFollowersMax:
        return False
    if ta.favorites < setting.followFavoritesMin or ta.favorites > setting.followFavoritesMax:
        return False
    return True

def get_person_list(r):
    personList = []
    for status in r.json()['statuses']:
        screen_name = status['user']['screen_name']
        followers = status['user']['followers_count']
        friends_count = status['user']['friends_count']
        favourites_count = status['user']['favourites_count']
        statuses_count = status['user']['statuses_count']
        a = TwitterAccount(screen_name, followers, friends_count, favourites_count, statuses_count)
        personList.append(a)
    return set(personList)

def get_search_q(setting):
    return setting.hashTags[random.randint(0, len(setting.hashTags) - 1)]