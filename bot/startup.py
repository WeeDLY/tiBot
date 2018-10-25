import argparse
import tiBot.main as main
import util.logger as logger
import util.settings as settings
import twitter.twitter as twitter
import imgur.imgur as imgur
import database.database as database
import debug.debug as debug

def startup(settingsFile, debugMode = False):
    setting = settings.Settings(settingsFile)
    if setting.check_all_settings() is False:
        logSettings.log(logger.LogLevel.INFO, 'Failed to load settings')
        return

    """ tiBot starting, that checks database, twitter and imgur """
    if debugMode:
        logSettings = logger.Logger(setting.logFileName, setting.logFolder, maxSize=setting.logSize, printLevel=logger.LogLevel.INFO)
    else:
        logSettings = logger.Logger(setting.logFileName, setting.logFolder, maxSize=setting.logSize, printLevel=setting.LOGGER_PRINT_LEVEL)
    logSettings.log(logger.LogLevel.INFO, 'tiBot is starting up', forcePrint=True)

    db = check_database(logSettings, setting.database)
    if db is None:
        logSettings.log(logger.LogLevel.CRITICAL, 'Database is not set up correctly. Exiting..')
        return

    twit = twitter.Twitter(logSettings, setting)
    twit.authenticated = twit.authenticate()
    if twit.authenticated is False:
        logSettings.log(logger.LogLevel.CRITICAL, 'Twitter is not authenticated. Exiting..')
        return
        
    imgr = imgur.Imgur(logSettings, setting)
    imgr.authenticated = imgr.authenticate()
    if imgr.authenticated is False:
        logSettings.log(logger.LogLevel.CRITICAL, 'Imgur is not authenticated. Exiting..')
        return
    if debugMode:
        logSettings.log(logger.LogLevel.INFO, 'Everything is set up, starting tiBot in debug mode..')
        debug.debug(logSettings, setting, db, twit, imgr)
    else:
        logSettings.log(logger.LogLevel.INFO, 'Everything is set up, starting tiBot..')
        main.start(logSettings, setting, db, twit, imgr)
    
def check_database(logSettings, databaseFile):
    db = database.Database(logSettings, databaseFile)
    checkDB = db.check_database()
    if checkDB is False:
        logSettings.log(logger.LogLevel.CRITICAL, 'Database is not set up correctly')
        return None
    return db

def parse_arguments():
    """ Parse command line arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--settings', type=str, required=True, help='Settings file')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Whether to start in debug mode')
    parser.set_defaults(debug=False)
    args = parser.parse_args()

    if args.debug:
        startup(args.settings, True)
    else:
        startup(args.settings)

if __name__ == '__main__':
    parse_arguments()
