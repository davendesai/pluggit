import os
import logging
from time import sleep

from ConfigParser import ConfigParser
from ConfigParser import Error as ConfigError

from threader import PluggitThreader
from handlers import PluggitHandler
from database import PluggitDatabase

import validate
from plugin import PluggitPlugin

class PluggitController:
    """
    reddit_bot is a the skaffolding that makes implementing reddit bots a more
    pleasant experience. Based on your implementation, it will monitor
    submissions and comments and take action. 
    """

    def __init__(self):
        # DEBUG mode
        self.debug = False
        
        # Create root logger
        logging.basicConfig()
        self.logger = logging.getLogger('PluggitController')

        self.logger.setLevel(logging.INFO)
        self.logger.info('logging started')

        # Load config
        self._load_config()
        
        # Create the global theader, network manager, and database
        self.threader = PluggitThreader()
        self.handler = PluggitHandler(debug = self.debug)
        self.database = PluggitDatabase(debug = self.debug)

        # Load plugins
        self.plugins = []
        self._discover_plugins()
        
        # Let the manager take over...
        self._process_old()
        self.threader.join_all() # Wait to catch up after sleep
        self._start_monitoring()
        
        # Periodically check for keyboard interrupts, etc...
        while True:
            sleep(5)

    def _load_config(self):
        path = 'config/pluggit.ini'
        filename = os.path.join(os.path.dirname(__name__), path)
        
        try:
            parser = ConfigParser()
            parser.read(filename)
            
            options = parser.options('pluggit')
            validate.pluggit_config(options)
            print options

            # DEBUG statement not strictly necessary, but would be nice...
            if 'debug' in options and parser.get('pluggit', 'debug') == '1':
                self.debug = True
            
            self.logger.info('loaded Pluggit configuration')
        except ConfigError as e:
            self.logger.error('no Pluggit config file found')
            exit(-1)
            
    def _discover_plugins(self):
        self.logger.info('started loading plugins...')
        path = os.path.join(os.path.dirname(__name__), 'plugins')
        
        # Get a list of plugins and keep track of them
        for root, dirs, files in os.walk(path):
            for filename in files:
                plugin_name, file_ext = os.path.splitext(filename)

                # Filter for Python files
                if file_ext == '.py' and not '__init__' in plugin_name:
                    package = __import__(path, fromlist = [plugin_name])
                    module = getattr(package, plugin_name)
                    self._load_plugin(module, plugin_name)
                    
        if len(self.plugins) == 0:
            self.logger.error('no plugins found to load. shutting down...')
            exit(-1)

        self.logger.info('completed loading {} plugin(s)'.format(len(self.plugins)))

    def _load_plugin(self, module, plugin_name):
        try:
            plugin = module.init(self.handler, self.database)
            self.logger.info('-----> detected {} plugin'.format(plugin.name))
            self._load_plugin_config(plugin, plugin_name)
            self.logger.info('-----> loaded {} configuration'.format(plugin.name))

            self.plugins.append(plugin)
        except Exception as e:
            self.logger.warning('an error occurred when trying to load {}'.format(plugin_name + '.py'))
            self.logger.warning('-----> ' + str(e))
        
    def _load_plugin_config(self, plugin, config_name):
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
            e._Error__message = 'no appropriate config file found'
            raise

    def _process_old(self):
        [self.threader.run_thread(plugin.process_old_submissions) for plugin in self.plugins]
        [self.threader.run_thread(plugin.process_old_comments) for plugin in self.plugins]
        
    def _start_monitoring(self):
        [self.threader.run_thread(plugin.monitor_submissions) for plugin in self.plugins]
        [self.threader.run_thread(plugin.monitor_comments) for plugin in self.plugins]
