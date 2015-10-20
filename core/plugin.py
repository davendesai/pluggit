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
        
    def configure(self, user_agent, sub_subs, com_subs):
        # Create PRAW Reddit API necessities
        self.reddit_session = praw.Reddit(user_agent = user_agent, handler = self.handler)
        
        # Dispense subreddit information
        self.submission_subreddits = map(str.strip, sub_subs.split(','))
        self.comment_subreddits = map(str.strip, com_subs.split(','))

    def submission_loop(self, subreddit):
        stream = praw.helpers.submission_stream(self.reddit_session, subreddit = subreddit, limit = 15)
        try:
            for submission in stream:
                self.logger.debug('{}: SUBMISSION: {}'.format(subreddit, submission.title))
                self.act_submission(submission)
        except Exception as e:
            self.logger.error('unable to contact reddit API.')
            self.logger.error('-----> ' + str(e))

    @abstractmethod
    def act_submission(self, submission):
        pass

    @abstractmethod
    def act_comment(self, comment):
        pass
