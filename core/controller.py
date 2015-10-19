import os
import logging

import praw
from praw.handlers import MultiprocessHandler

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
        self.logger.info('logging started')

        # Create the thread manager
        self.threader = RedditThreader()

        # Load plugins
        self.plugins = []
        self.load_plugins()
        
        # Let the manager take over...
        self.spawn_threads()
        self.threader.join_all_threads()

    def load_plugins(self):
        self.logger.info('started loading plugins...')
        path = 'plugins'
        
        # Get a list of plugins and keep track of them
        for root, dirs, files in os.walk(path):
            for filename in files:
                plugin_name, file_ext = os.path.splitext(filename)

                # Filter for Python files
                if file_ext == '.py' and not '__init__' in plugin_name:
                    package = __import__(path, fromlist = [plugin_name])
                    module = getattr(package, plugin_name)

                    try:
                        plugin = module.init()
                        plugin.config = self.load_config(plugin_name)
                        plugin.configure()
                        
                        self.logger.info('detected and loaded plugin in {}'.format(filename))

                        self.plugins.append(plugin)
                    except Exception as e:
                        self.logger.warning('an error occurred when trying to load {}'.format(filename))
                        self.logger.warning('-----> ' + str(e))
                    
        if len(self.plugins) == 0:
            self.logger.error('no plugins found to load. shutting down...')
            exit(-1)

        self.logger.info('completed loading {} plugin(s)'.format(len(self.plugins)))

    def load_config(self, proposed):
        path = 'config'
        required = proposed.lower() + '_config'

        # Get a list of all configuration files
        for root, dirs, files in os.walk(path):
            for filename in files:
                config_name, file_ext = os.path.splitext(filename)

                # Filter for Python files
                if  file_ext == '.py' and config_name == required:
                    package = __import__(path, fromlist = [config_name])
                    module = getattr(package, config_name)

                    return module

        raise Exception('no config file found for {}'.format(proposed))

    def spawn_threads(self):
        for plugin in self.plugins:
            for subreddit in plugin.submission_subreddits:
                if not self.threader.thread_exists(subreddit, submission = True):
                    self.threader.run_thread('{} submissions'.format(subreddit), plugin.submission_loop)
