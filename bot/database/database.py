import database.query as query
import sqlite3
import sys
sys.path.append("..")
import util.logger as logger

class Database():
    """ Database class """
    def __init__(self, logger, databaseFile):
        self.databaseFile = databaseFile
        self.connection = sqlite3.connect(self.databaseFile, check_same_thread=False)
        self.logger = logger
    
    def check_database(self):
        """ Checks and/or creates the tables in the database """
        self.logger.log(logger.LogLevel.INFO, 'Checking database tables')
        table_stats = self.check_table(query.TABLE_STATS, query.QUERY_CREATE_TABLE_STATS())
        if table_stats is False:
            return False
        table_tweets = self.check_table(query.TABLE_TWEETS, query.QUERY_CREATE_TABLE_TWEETS())
        if table_tweets is False:
            return False
        table_posts = self.check_table(query.TABLE_POSTS, query.QUERY_CREATE_TABLE_POSTS())
        if table_posts is False:
            return False
        table_follows = self.check_table(query.TABLE_FOLLOWS, query.QUERY_CREATE_TABLE_FOLLOWS())
        if table_follows is False:
            return False
        return True
        
    def check_table(self, table, createTableQuery, maxAttempts=3):
        """ Checks and/or creates an individual table """
        tableSetUp = False
        i = 0
        while tableSetUp is False or i > maxAttempts:
            self.logger.log(logger.LogLevel.INFO, 'Checking table(%d): %s' % (i, table))
            tableExists = self.query_exists(query.QUERY_TABLE_EXISTS(), (table, ))
            if tableExists is False:
                self.logger.log(logger.LogLevel.INFO, 'Creating table(%d): %s' % (i, table))
                self.query_commit(createTableQuery)
            else:
                return True
            i += 1
        if tableSetUp is False:
            self.logger.log(logger.LogLevel.CRITICAL, 'Could not create table: %s' % table)
        return tableSetUp

    def query_fetchall(self, q, param=None):
        """ Queries database and returns all """
        try:
            c = self.connection.cursor()
            if param is None:
                c.execute(q)
            else:
                c.execute(q, param)
            self.logger.log(logger.LogLevel.DEBUG, 'database.fetchall: %s | %s' % (q, param))            
            return c.fetchall()
        except Exception as e:
            self.logger.log(logger.LogLevel.ERROR, 'database.fetchall: %s. %s | %s' % (e, q, param))
            return False

    def query_fetchone(self, q, param=None):
        """ Queries database and return one row """
        try:
            c = self.connection.cursor()
            if param is None:
                c.execute(q)
            else:
                c.execute(q, param)
            self.logger.log(logger.LogLevel.DEBUG, 'database.fetchone: %s | %s' % (q, param))            
            return c.fetchone()
        except Exception as e:
            self.logger.log(logger.LogLevel.ERROR, 'database.fetchone: %s. %s | %s' % (e, q, param))
            return False

    def query_exists(self, q, param=None):
        """ checks if the query yields a result """
        """ Queries database and return one row """
        try:
            c = self.connection.cursor()
            c.execute(q, param)
            self.logger.log(logger.LogLevel.DEBUG, 'database.query_exists: %s | %s' % (q, param))            
            if c.fetchone() is None:
                return False
            else:
                return True
        except Exception as e:
            self.logger.log(logger.LogLevel.ERROR, 'database.query_exists: %s. %s | %s' % (e, q, param))
            return False

    def database_dump(self):
        """ Dumps all tables in the database """
        print('=====Dumping database=====')
        self.database_table_dump(query.TABLE_STATS)
        print()
        self.database_table_dump(query.TABLE_TWEETS)
        print()
        self.database_table_dump(query.TABLE_POSTS)
        print()
        self.database_table_dump(query.TABLE_FOLLOWS)

    def database_table_dump(self, tableName):
        try:
            c = self.connection.cursor()
            print('=====%s=====' % tableName)
            for row in c.execute('SELECT * FROM %s' % tableName):
                print(row)
        except Exception as e:
            self.logger.log(logger.LogLevel.ERROR, 'Error database.database_table_dump: %s' % e)

    def query_commit(self, q, param=None):
        """ Executes a query, returns True if executed, otherwise False """
        try:
            c = self.connection.cursor()
            if param is None:
                c.execute(q)
            else:
                c.execute(q, param)
            self.logger.log(logger.LogLevel.DEBUG, 'database.query_commit: %s | %s' % (q, param), True)
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.log(logger.LogLevel.ERROR, 'database.query_commit: %s' % e)
            return False