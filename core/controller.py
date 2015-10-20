import os
import logging

from ConfigParser import ConfigParser
from ConfigParser import Error as ConfigError

import praw

from threader import PluggitThreader
from handler import PluggitHandler
from plugin import PluggitPlugin

class PluggitController:
    """
    reddit_bot is a the skaffolding that makes implementing reddit bots a more
    pleasant experience. Based on your implementation, it will monitor
    submissions and comments and take action. 
    """

    def __init__(self):
        # Create root logger
        logging.basicConfig()
        self.logger = logging.getLogger('PluggitController')

        self.logger.setLevel(logging.INFO)
        self.logger.info('logging started')

        # Create the global thread manager and network handler
        self.threader = PluggitThreader()
        self.handler = PluggitHandler()

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
                        plugin = module.init(self.handler)
                        self.logger.info('-----> detected plugin in {}'.format(filename))
                        
                        self.load_config(plugin, plugin_name)
                        self.plugins.append(plugin)
                    except Exception as e:
                        self.logger.warning('-----> an error occurred when trying to load {}'.format(filename))
                        self.logger.warning('----------> ' + str(e))
                    
        if len(self.plugins) == 0:
            self.logger.error('no plugins found to load. shutting down...')
            exit(-1)

        self.logger.info('completed loading {} plugin(s)'.format(len(self.plugins)))

    def load_config(self, plugin, config_name):
        path = 'config/' + config_name.lower() + '.ini'
        filename = os.path.join(os.path.dirname(__name__), path)
        
        try:
            parser = ConfigParser()
            parser.read(filename)
            options_available = parser.options('app')

            # DEBUG statement not strictly necessary, but would be nice...
            if 'debug' in options_available and parser.get('app', 'debug') == '1':
                plugin.logger.info('entering debug mode')
                plugin.logger.setLevel(logging.DEBUG)
            
            # Check required options
            assert 'user_agent' in options_available, 'unable to find user agent'
            assert 'submission_subreddits' in options_available, 'unable to find submission_subreddits'
            assert 'comment_subreddits' in options_available, 'unable to find comment_subreddits'

            plugin.configure(parser.get('app', 'user_agent'),
                             parser.get('app', 'submission_subreddits'),
                             parser.get('app', 'comment_subreddits'))

        except ConfigError as e:
            if e._Error__message == 'No section: \'app\'':
                raise Exception('no config file found')
        except Exception as e:
            raise Exception('config error: ' + str(e))

    def spawn_threads(self):
        for plugin in self.plugins:
            for subreddit in plugin.submission_subreddits:
                if not self.threader.thread_exists(subreddit):
                    self.threader.run_thread('{} submissions'.format(subreddit),
                                             plugin.submission_loop, subreddit)
