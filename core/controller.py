import os
import logging
from pprint import pprint
from socket import error as SocketError

import praw
from praw.handlers import MultiprocessHandler

from config import config
from threader import RedditThreader
from plugin import RedditPlugin

class RedditBotController:
    """
    reddit_bot is a the skaffolding that makes implementing reddit bots a more
    pleasant experience. Based on your implementation, it will monitor
    submissions and comments and take action. 
    """

    def __init__(self):
        # Create root logger
        logging.basicConfig()
        self.logger = logging.getLogger('RedditBotController')

        self.logger.setLevel(logging.INFO)
        if config.DEBUG == 1:
            self.logger.setLevel(logging.DEBUG)
            
        self.logger.info('logging started')

        # Create PRAW Multiprocess handler
        try:
            self.handler = MultiprocessHandler()
            self.logger.info('created grobal multiprocess handler')
        except ClientException as e:
            self.logger.error('unable to create multiprocess handler. shutting down...')
            self.logger.error(e)
            exit(-1)

        # Create data streams
        try:
            self.submission_session = praw.Reddit(user_agent = config.USER_AGENT, handler = self.handler)
            self.comment_session = praw.Reddit(user_agent = config.USER_AGENT, handler = self.handler)
            self.logger.info('PRAW reddit sessions initialized')

            self.submission_stream = praw.helpers.submission_stream(self.submission_session,
                                                                    config.SUBREDDIT,
                                                                    limit = config.SUBMISSION_LIMIT)
            self.comment_stream = praw.helpers.comment_stream(self.comment_session,
                                                              config.SUBREDDIT,
                                                              limit = config.COMMENT_LIMIT)
            self.logger.info('created reddit data streams')
        except SocketError as e:
            self.logger.error('unable to contact reddit API. shutting down...')
            self.logger.error(e)
            exit(-1)

        # Load plugins
        self.plugins = []
        self.load_plugins()
        
        # Start monitoring threads
        self.threader = RedditThreader()

        if config.SUBMISSIONS_ENABLED == 1:
            self.threader.start('submission_thread', self.submission_thread)

        if config.COMMENTS_ENABLED == 1:
            self.threader.start('comment_thread', self.comment_thread)

        self.threader.join()

    def load_plugins(self):
        path = config.PLUGIN_LOCATION
        
        # Get a list of plugins and keep track of them
        for root, dirs, files in os.walk(path):
            for filename in files:
                plugin_name, file_ext = os.path.splitext(filename)

                # Filter for Python files
                if not '__init__' in filename and file_ext == '.py':
                    package = __import__(path, fromlist = [plugin_name])
                    module = getattr(package, plugin_name)

                    try:
                        plugin = module.init(self.handler)

                        if isinstance(plugin, RedditPlugin):
                            self.plugins.append(plugin)
                            self.logger.info('detected and loaded {} plugin'.format(plugin.name))
                    except Exception as e:
                        self.logger.warning(e)
                    
        if len(self.plugins) == 0:
            self.logger.error('no plugins found to load. shutting down...')
            exit(-1)
                    
    def submission_thread(self):
        self.logger.info('processing submissions')

        try:
            for submission in self.submission_stream:
                self.logger.debug('SUBMISSION: ' + submission.body)
                self.distribute(submission)
        except SocketError as e:
            self.logger.error('praw multiprocess server is not running. shutting down...')
            self.logger.error(e)
            exit(-1)

    def comment_thread(self):
        self.logger.info('processing comments')

        try:
            for comment in self.comment_stream:
                self.logger.debug('COMMENT: ' + comment.body)
                self.distribute(comment)
        except SocketError as e:
            self.logger.error('praw multiprocess server is not running. shutting down...')
            self.logger.error(e)
            exit(-1)

    def distribute(self, thing):
        # Pass it along to the plugins
        for plugin in self.plugins:
            self.act(plugin, thing)

    def act(self, plugin, thing):
        # Take action depending on 'thing' type
        try:
            if isinstance(thing, praw.objects.Submission):
                plugin.act_submission(thing)
            elif isinstance(thing, praw.objects.Comment):
                plugin.act_comment(thing)
        except Exception as e:
            self.logger.warning('an error occured in the {} plugin'.format(plugin.name))
            self.logger.warning(e)
