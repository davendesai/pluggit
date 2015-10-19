import os
import logging
from abc import ABCMeta, abstractmethod
from socket import error as SocketError

import praw
from praw.handlers import MultiprocessHandler

class RedditPlugin():
    """
    plugin_base is the base class from which all plugins must inherit.
    It provides a common starting point which implements some necessary
    features like logging and abstracts away some of the more complicated
    functionality from the plugin creator.
    """

    __metaclass__ = ABCMeta

    def __init__(self, name):
        # Create local variables
        self.submission_subreddits = []
        self.comment_subreddits = []
        
        # Create plugin logger
        self.logger = logging.getLogger(name)

        # Load config from file
        self.config = None

        # Create Reddit API necessities
        self.reddit_session = None

    def configure(self):
        # DEBUG statement not strictly necessary, but would be nice...
        if not hasattr(self.config, 'DEBUG') or self.config.DEBUG == 0:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.DEBUG)
            
        # Check for most important variables
        assert hasattr(self.config, 'USER_AGENT'), 'unable to find user agent'
        assert hasattr(self.config, 'SUBMISSION_SUBREDDITS'), 'unable to find submission subreddits'
        assert hasattr(self.config, 'COMMENT_SUBREDDITS'), 'unable to find comment subreddits'

        # Create PRAW Reddit API necessities
        self.reddit_session = praw.Reddit(user_agent = self.config.USER_AGENT)
        
        # Dispense subreddit information
        subreddits = self.config.SUBMISSION_SUBREDDITS.split(',')
        self.submission_subreddits = map(str.strip, subreddits)
            
        subreddits = self.config.COMMENT_SUBREDDITS.split(',')
        self.comment_subreddits = map(str.strip, subreddits)

    def submission_loop(self):
        try:
            for submission in submission_stream:
                self.logger.debug('SUBMISSION: ' + submission.title)
                self.act_submission(submission)
        except Exception as e:
            self.logger.error('unable to contact reddit API.')
            self.logger.error(e)

    @abstractmethod
    def act_submission(self, submission):
        pass

    @abstractmethod
    def act_comment(self, comment):
        pass
