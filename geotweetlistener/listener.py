import os
import json
import logging
from datetime import datetime
import peewee
import pymysql
from tweepy import Stream
from tweepy.streaming import StreamListener
from tweepy.auth import OAuthHandler

# This is necessary to create Tweet Class,
# database is then set at runtime from config
database = peewee.MySQLDatabase(None)


class GeoTweetListener(StreamListener):

    def __init__(self, config):

        self.config = config
        self.database = database

        # Initialize
        self._initialize_logging()
        self._initialize_output()

    def _initialize_logging(self):
        """ Set up logging to file """
        log_folder = os.path.join(self.config.get('logging', 'log_folder'), '')
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        logging.basicConfig(filename=log_folder + 'log.log',
                            level=logging.INFO)

    def _initialize_output(self):
        """ Set up data saving """
        if self.config.get('database', 'database_type') == 'mysql':
            self._create_sql_database_connection()
        if self.config.get('database', 'database_type') == 'csv':
            self._create_output_file()

    def _create_output_file(self):
        """ Create output file if it doesn't exist """
        csv_path = os.path.join(self.config.get('database', 'csv_path'), '')
        if not os.path.exists(csv_path):
            os.makedirs(csv_path)
        if not os.path.isfile(csv_path + 'tweets_data.csv'):
            save_file = open(csv_path + 'tweets_data.csv',
                             'w', encoding='utf-8')
            header = ['created_at', 'tweet_id', 'user_id', 'lat', 'lon']
            save_file.write(';'.join([str(i) for i in header]))
            save_file.write(u'\n')
            save_file.close()

    def _create_sql_database_connection(self):
        """ Set up the connection to the mysql database """
        dbname = self.config.get('mysql', 'dbname')
        user = self.config.get('mysql', 'user')
        host = self.config.get('mysql', 'host')
        password = self.config.get('mysql', 'password')
        # Create database if it doesn't exist
        conn = pymysql.connect(host=host, user=user,
                               password=password)

        conn.cursor().execute('CREATE DATABASE IF NOT EXISTS {}'.format(dbname))
        conn.close()

        # Initialize database and create tweet table
        self.database.init(dbname, host=host, user=user, password=password)
        self.database.create_tables([Tweet], True)
        logging.info("{} - Database connection established".format(
            datetime.now()))

    def on_status(self, status):
        """ Log status """
        logging.info("{} - Status update: {}".format(datetime.now(),
                                                     status.text))

    def on_error(self, status_code):
        """ Log error code and stop process """
        logging.warning("{} - Error: Error Code {}".format(datetime.now(),
                                                           status_code))

    def on_timeout(self):
        """ Called if timeout signal received in stream.
        Log event and continue """
        logging.warning("{} - Timeout".format(datetime.now()))

    def on_data(self, data):
        """ If a tweet is reveiced from stream, save data """
        tweet = json.loads(data)

        try:
            coordinates = tweet['coordinates']
            if coordinates:  # If tweet contains location, save
                self._save_tweet(tweet)
        except TypeError as err:
            logging.warning("{} - Unable to save tweet: {}".format(
                datetime.now(), err))

    def _save_tweet(self, tweet):
        """ Save the content of a given tweet """

        user_id = tweet['user']['id']
        tweet_id = tweet['id']
        created_at = tweet['created_at']
        location = tweet['coordinates']['coordinates']
        lon = location[0]
        lat = location[1]

        if self.config.get('database', 'database_type') == 'mysql':
            created_datetime = datetime.strptime(created_at,
                                                 '%a %b %d %H:%M:%S +0000 %Y')
            tweet = Tweet(created_at=created_datetime, user_id=user_id,
                          tweet_id=tweet_id, lat=lat, lon=lon)
            tweet.save()

        elif self.config.get('database', 'database_type') == 'csv':
            save_data = [created_at, user_id, tweet_id, lat, lon]
            csv_path = os.path.join(self.config.get('database', 'csv_path'), '')
            save_file = open(csv_path + 'tweets_data.csv',
                             'a', encoding='utf-8')
            save_file.write(';'.join([str(i) for i in save_data]))
            save_file.write(u'\n')
            save_file.close()

    def start_streaming(self):
        """ Start streaming and saving Tweets """
        logging.info("{} - Starting new stream".format(datetime.now()))

        # Set up authentication
        consumer_key = self.config.get('twitter', 'consumer_key')
        consumer_secret = self.config.get('twitter', 'consumer_secret')
        access_token = self.config.get('twitter', 'access_token')
        access_token_secret = self.config.get('twitter', 'access_token_secret')

        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        bounding_box = [float(i) for i in
                        self.config.get('location', 'bounding_box').split(',')]

        # Start stream
        stream = Stream(auth, self)
        stream.filter(locations=bounding_box)


class Tweet(peewee.Model):
    """ Model for MySQL Table """
    created_at = peewee.TimestampField()
    user_id = peewee.BigIntegerField()
    tweet_id = peewee.BigIntegerField()
    lat = peewee.FloatField()
    lon = peewee.FloatField()

    class Meta:
        database = database
