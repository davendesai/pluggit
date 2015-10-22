import logging
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

    def __init__(self, name, handler):
        self.name = name
        self.handler = handler
        
        # Create plugin logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create Reddit API necessities
        self.reddit_session = None
        self.oauth = None

        self.submission_subreddits = []
        self.comment_subreddits = []

        # Create database handle for later
        self.database = None
        
    def configure(self, configfile, debug, user_agent, s_subreddits, c_subreddits):
        if debug == True:
            self.logger.info('entering debug mode')
            self.logger.setLevel(logging.DEBUG)
            
        # Create PRAW Reddit API necessities
        self.reddit_session = praw.Reddit(user_agent = user_agent, handler = self.handler)

        # Authenticate
        self.logger.info('<----------> OAUTH2 SETUP <---------->')
        self.oauth = OAuth2Util(self.reddit_session, configfile = configfile, server_mode = True)

        # Force authentication once, then every hour
        self.oauth.refresh(force = True)
        self.logger.info('<----------> OAUTH2 COMPLETE <------->')
        
        # Dispense subreddit information
        self.submission_subreddits = [subreddit.strip() for subreddit in s_subreddits.split(',')] 
        self.comment_subreddits = [subreddit.strip() for subreddit in c_subreddits.split(',')]

        # Create database connection
        self.database = PluggitDatabase(__name__)
        
        # Dispense user stored information


    def submission_loop(self):
        subreddits = '+'.join(self.submission_subreddits)
        stream = praw.helpers.submission_stream(self.reddit_session, subreddits, limit = 15)
        try:
            for submission in stream:
                self.logger.debug('{}: SUBMISSION: {}'.format(submission.subreddit, submission.title))
                self.act_submission(submission)
        except Exception as e:
            self.logger.error('unable to contact reddit API.')
            self.logger.error('-----> ' + str(e))
            
    def comment_loop(self):
        pass

    @abstractmethod
    def act_submission(self, submission):
        pass

    @abstractmethod
    def act_comment(self, comment):
        pass
