import logging
from abc import ABCMeta, abstractmethod

import praw

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

        # Load config from file
        self.config = None

        # Create Reddit API necessities
        self.reddit_session = None

        self.submission_subreddits = []
        self.comment_subreddits = []
        
    def configure(self):
        # DEBUG statement not strictly necessary, but would be nice...
        if not hasattr(self.config, 'DEBUG'):
            self.logger.warning('no debug variable found. maybe a good idea to have one?')
        elif self.config.DEBUG == 1:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug('debug mode enabled')
            
        # Check for most important variables
        assert hasattr(self.config, 'USER_AGENT'), 'unable to find user agent'
        assert hasattr(self.config, 'SUBMISSION_SUBREDDITS'), 'unable to find submission subreddits'
        assert hasattr(self.config, 'COMMENT_SUBREDDITS'), 'unable to find comment subreddits'

        # Create PRAW Reddit API necessities
        self.reddit_session = praw.Reddit(user_agent = self.config.USER_AGENT, handler = self.handler)
        
        # Dispense subreddit information
        subreddits = self.config.SUBMISSION_SUBREDDITS.split(',')
        self.submission_subreddits = map(str.strip, subreddits)
        self.logger.debug('monitoring submission on {}'.format(self.submission_subreddits))
            
        subreddits = self.config.COMMENT_SUBREDDITS.split(',')
        self.comment_subreddits = map(str.strip, subreddits)
        self.logger.debug('monitoring comments on {}'.format(self.comment_subreddits))

    def submission_loop(self, subreddit):
        stream = praw.helpers.submission_stream(self.reddit_session, subreddit = subreddit, limit = 15)
        try:
            for submission in stream:
                self.logger.debug('{}: SUBMISSION: {}'.format(subreddit, submission.title))
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
