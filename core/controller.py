import os
import logging
from time import sleep

from ConfigParser import ConfigParser
from ConfigParser import Error as ConfigError

import validate
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

        # Create the global theader and network manager
        self.threader = PluggitThreader()
        self.handler = PluggitHandler()

        # Load plugins
        self.plugins = []
        self.load_plugins()
        
        # Let the manager take over...
        self.spawn_threads()
        while True:
            sleep(5)
            
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
                        self.logger.info('-----> detected {} plugin'.format(plugin.name))
                        self.load_plugin_config(plugin, plugin_name)

                        self.plugins.append(plugin)
                    except Exception as e:
                        self.logger.warning('an error occurred when trying to load {}'.format(filename))
                        self.logger.warning('-----> ' + str(e))
                    
        if len(self.plugins) == 0:
            self.logger.error('no plugins found to load. shutting down...')
            exit(-1)

        self.logger.info('completed loading {} plugin(s)'.format(len(self.plugins)))

    def load_plugin_config(self, plugin, config_name):
        path = 'config/' + config_name.lower() + '.ini'
        filename = os.path.join(os.path.dirname(__name__), path)
        
        try:
            parser = ConfigParser()
            parser.read(filename)
            
            options = parser.options('app')
            validate.plugin_config(options)

            # DEBUG statement not strictly necessary, but would be nice...
            debug = False
            if 'debug' in options and parser.get('app', 'debug') == '1':
                debug = True
            
            plugin.configure(filename, debug,
                             parser.get('app', 'user_agent'),
                             parser.get('app', 'submission_subreddits'),
                             parser.get('app', 'comment_subreddits'))

        except ConfigError as e:
            e._Error__message = 'no config file found'
            raise

    def spawn_threads(self):
        for plugin in self.plugins:
            self.threader.run_thread(plugin.submission_loop)
            self.threader.run_thread(plugin.comment_loop)
