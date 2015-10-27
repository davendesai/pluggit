import logging
from time import sleep
from abc import ABCMeta, abstractmethod

import praw
from OAuth2Util import OAuth2Util

from database import PluggitDatabase

class PluggitPlugin():
    """
    plugin_base is the base class from which all plugins must inherit.
    It provides a common starting point which implements some necessary
    features like logging and abstracts away some of the more complicated
    functionality from the plugin creator.
    """

    __metaclass__ = ABCMeta

    def __init__(self, name, handler, database):
        self.name = name
        self.handler = handler
        self.database = database
        
        # Create plugin logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create Reddit API necessities
        self.reddit_session = None
        self.oauth = None

        self.submission_subreddits = []
        self.comment_subreddits = []
        
    def configure(self, configfile, debug, user_agent, s_subreddits, c_subreddits):
        if debug == True:
            self.logger.setLevel(logging.DEBUG)
            
        # Create PRAW Reddit API necessities
        self.reddit_session = praw.Reddit(user_agent = user_agent, handler = self.handler)

        # Authenticate
        self.oauth = OAuth2Util(self.reddit_session, configfile = configfile, server_mode = True)

        # Force authentication once, then every hour
        self.oauth.refresh(force = True)

        self.logger.info('<----------> OAUTH2 SETUP <---------->')
        
        # Dispense subreddit information
        self.submission_subreddits = [subreddit.strip() for subreddit in s_subreddits.split(',')] 
        self.comment_subreddits = [subreddit.strip() for subreddit in c_subreddits.split(',')]

    def get_stream(self, stream, target, ignore_list):
        try:
            [target(item) for item in stream if not item.id in ignore_list]
        except Exception as e:
            self.logger.error('an error occurred with item id: {}'.format(item.id))
            self.logger.error('-----> ' + str(e))

    def process_old_submissions(self):
        subreddits = '+'.join(self.submission_subreddits)
        subreddit_obj = self.reddit_session.get_subreddit(subreddits)

        latest_submission = self.database.get_latest_submission(self.name)
        if latest_submission == None:
            return
        latest_id = latest_submission['id']

        self.logger.info('<----------> OLD SUBMISSIONS <------->')

        submission_list = subreddit_obj.get_new(place_holder = latest_id, limit = None)
        self.get_stream(submission_list, self.act_submission, [latest_id])

    def monitor_submissions(self):
        subreddits = '+'.join(self.submission_subreddits)
        stream = praw.helpers.submission_stream(self.reddit_session, subreddits, limit = 10)

        self.logger.info('<----------> NEW SUBMISSIONS <------->')
        
        latest_submissions = self.database.get_many_latest_submissions(self.name)

        # Ignore already processed due to overlap
        ignore_list = None
        if not latest_submissions == None:
            ignore_list = [submission['id'] for submission in latest_submissions]
            
        while True:
            self.get_stream(stream, self.act_submission, ignore_list)
            
    def act_submission(self, submission):
        self.logger.debug('{}: SUBMISSION: {}'.format(submission.subreddit, submission.title))
        self.database.store_latest_submission(self.name, submission)

        # Pass onto plugin
        self.received_submission(submission)

    @abstractmethod
    def received_submission(self, submission):
        pass
            
    def process_old_comments(self):
        pass
            
    def monitor_comments(self):
        pass

    def act_comment(self, comment):
        pass

    @abstractmethod
    def received_comment(self, comment):
        pass
