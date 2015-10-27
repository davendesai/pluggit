import os
import logging

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidURI

from models import PluggitSubmission, PluggitComment

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
        
        # Create client for interfacing with database
        self.mongoclient = None

        hostpath = 'mongodb://localhost:27017'
        if hasattr(os.environ, 'MONGOLAB_URI'):
            hostpath = os.environ['MONGOLAB_URI']

        try:
            self.mongoclient = MongoClient(hostpath)
            self.logger.info('database connection initialized')
        except InvalidURI as e:
            self.logger.error('the database URI was malformed. check it please?')
            raise
        except Exception as e:
            self.logger.error('unable to connect to the database')
            exit(-1)
            
    def __del__(self):
        if not self.mongoclient == None:
            self.mongoclient.close()
        
    def store_submission(self, collection, submission):
        data = PluggitSubmission(submission).__dict__
        collection.insert_one(data)
        
    def store_latest_submission(self, name, submission):
        database = self.mongoclient[name]
        collection = database.latest_submission

        self.store_submission(collection, submission)

        if collection.count() > 15:
            to_remove = collection.find_one(sort = [('created_utc', pymongo.ASCENDING)])
            collection.delete_one(to_remove)

    def get_latest_submission(self, name):
        database = self.mongoclient[name]
        collection = database.latest_submission

        if collection.count() == 0:
            return None
        return collection.find_one(sort = [('created_utc', pymongo.DESCENDING)])

    def get_many_latest_submissions(self, name):
        database = self.mongoclient[name]
        collection = database.latest_submission

        if collection.count() == 0:
            return None
        return collection.find()
        
