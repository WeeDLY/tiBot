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
TODO: Write about settings.json file

## Server
Python flask server.
Website with statistics about the state of the bot.

### Overall
General information, such as:

1. Current time
2. Twitter name
3. Runtime
4. Last tweet
5. + General twitter statistics..


### Query
Can query the database directly and fetch the result.
Will NOT commit the queries.

### Debug
Able to read the log files the bot produces from the website

### About
General information