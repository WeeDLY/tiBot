from flask import Flask, Markup, render_template, request
import sqlite3, datetime
import argparse
import subprocess, re
import glob, json, os

app = Flask(__name__)

twitterName = None
database = None
logFolder = None
connection = None
chartColumns = 14


@app.route('/')
def root():
    cur = connection.cursor()

    currentTime = datetime.datetime.now()
    cur.execute("select tweetDate from tweets order by tweetDate desc limit 1")
    lastTweet = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tweets")
    tweets = cur.fetchone()[0]
    cur.execute("select count(*) from follows where followingNow = 1")
    following = cur.fetchone()[0]
    cur.execute("select followers, favorites from stats order by lastUpdate desc limit 1")
    res = cur.fetchone()
    followers, likes = res[0], res[1]

    cur.execute("select sum(retweets), sum(favorites) from tweets")
    res = cur.fetchone()
    retweets, tweetLikes = res[0], res[1]

    timespan = datetime.timedelta(days=14) # 14days, because we update tweet 1week after it's posted
    endDate = datetime.datetime.now() - timespan
    cur.execute("select sum(retweets), sum(favorites) from tweets where tweetDate >= ?", (endDate, ))
    res = cur.fetchone()
    retweetsLastWeek, tweetLikesLastWeek = res[0], res[1]

    cur.execute("select lastUpdate, followers from stats order by lastUpdate desc limit %d" % chartColumns)
    result = cur.fetchall()
    labels = []
    values = []
    for strDate, followersDB in result:
        date = datetime.datetime.strptime(strDate, '%Y-%m-%d %H:%M:%S.%f')
        labels.append(date.strftime("%d/%m/%y"))
        values.append(followersDB)
    labels.reverse()
    values.reverse()

    botRuntime = get_bot_running()

    return render_template('main_page.html', twitterName=twitterName, currentTime=currentTime, botRuntime=botRuntime, lastTweet=lastTweet, 
                            tweets=tweets, following=following, followers=followers, likes=likes,
                            retweets=retweets, tweetLikes=tweetLikes, retweetsLastWeek=retweetsLastWeek, tweetLikesLastWeek=tweetLikesLastWeek,
                            values=values, labels=labels)

def get_runtime(start):
    try:
        return "%s uptime" % str(datetime.datetime.now() - datetime.datetime.strptime(start, "%a %b %d %H:%M:%S %Y"))
    except:
        return None

def get_bot_running():
    ps = subprocess.Popen('ps -eo pid,lstart,cmd | egrep "python3 startup\.py.+settings.json"',
                            shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read().decode()
    ps.stdout.close()
    ps.wait()
    output = output.split('python3 startup.py')[0]
    if output == "":
        return "Bot is not running"
    
    pid = re.search('\d+', output).group()
    ps = subprocess.Popen('ps -o etime= -p "%s"' % pid, shell=True, stdout=subprocess.PIPE)
    out = ps.stdout.read().decode()
    ps.stdout.close()
    ps.wait()
    return ''.join(out.split())

@app.route("/query", methods=["POST", "GET"])
def query():
    result = []
    tableHeader = []
    if request.method == "POST":
        query = request.form["query"]
        try:
            cur = connection.cursor()
            cur.execute(query)
            queryResult = cur.fetchall()
            if queryResult is None:
                result = "No result matched: %s" % query
                tableHeader = ""
            else:
                for desc in cur.description:
                    tableHeader.append(desc[0])
                result = queryResult
        except Exception as e:
            result = "Could not execute query: %s" % e
    
    return render_template('query.html', twitterName=twitterName, tableHeader=tableHeader, result=result)

@app.route("/debug")
def debug():
    files = get_files(logFolder)
    content = ""
    fileRequest = request.args.get("file")
    if fileRequest == None:
        return render_template('debug.html', twitterName=twitterName, files=files, content=content)

    if '..' in fileRequest:
        content = "._."
    else:
        content = read_content('%s/%s' % (logFolder, fileRequest))
    return render_template('debug.html', twitterName=twitterName, files=files, content=content)

def get_files(folder):
    files = glob.glob('%s/*' % folder)
    return [file.replace(folder, "") for file in files]

def read_content(file):
    try:
        with open(file, 'r') as f:
            return f.read()
    except:
        return "._."

@app.route("/about")
def about():
    return render_template('about.html', twitterName=twitterName)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--settings', type=str, required=True, help='Settings file')
    args = parser.parse_args()
    read_settings(args.settings)

def read_settings(settingsFile):
    global twitterName, database, logFolder, connection

    if os.path.isfile(settingsFile) is False:
        print('%s does not exist. Exiting' % settingsFile)
        exit()
    try:
        settingsData = open(settingsFile)
        data = json.load(settingsData)
        twitterName = data["twitterName"]
        database = data["database"]
        logFolder = data["logFolder"]
        connection = sqlite3.connect(database, check_same_thread=False)
        print('Loaded settings')
    except Exception as e:
        print(e)
        exit()

if __name__ == "__main__":
    parse_arguments()
    app.run(host='0.0.0.0', port=5000)