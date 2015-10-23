import os
import logging

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidURI

class PluggitDatabase:
    """
    database is the single store for all plugins using Pluggit. It provides a
    central place to store the ids that were processed during uptime. It allows
    for Pluggit to work regardless of network or system fluctuations.
    """

    def __init__(self):
        # Create logger
        self.logger = logging.getLogger('PluggitDatabase')
        self.logger.setLevel(logging.INFO)
        
        self.mongoclient = None
        hostpath = 'mongodb://localhost:27017'
        #hostpath = os.environ['MONGOLAB_URI']

        try:
            #mongoengine.connect(name, host = os.environ['MONGOLAB_URI'])
            self.mongoclient = MongoClient(hostpath)
            self.logger.info('database connection initialized')
        except InvalidURI as e:
            self.logger.error('the database URI was malformed. check it please?')
            raise
        except ConnectionFailure as e:
            self.logger.error('unable to connect to the database')
            raise

    def __del__(self):
        if not self.mongoclient == None:
            self.mongoclient.close()
        
    def store_submission(self, name, submission):
        database = self.mongoclient[name]
        collection = database.submissions

        data = {}
        data['id'] = submission.id
        data['title'] = submission.title
        data['date'] = submission.created_utc

        collection.insert_one(data)
        self.logger.info(' STORED SUB: {}'.format(submission.id))

        # Evict older entries
        if collection.count() > 5:
            collection.delete_one(collection.find_one())

    def get_newest_submission(self, name):
        database = self.mongoclient[name]
        collection = database.submissions

        if collection.count() == 0:
            return None
        return collection.find_one(sort = [('date', pymongo.DESCENDING)])['id']
        
