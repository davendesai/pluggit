import os
import logging
from abc import ABCMeta, abstractmethod, abstractproperty

from config import config

class RedditPlugin():
    """
    plugin_base is the base class from which all plugins must inherit.
    It provides a common starting point which implements some necessary
    features like logging and abstracts away some of the more complicated
    functionality from the plugin creator.
    """

    __metaclass__ = ABCMeta

    def __init__(self, name, handler):
        self.name = name
        
        # Create plugin logger
        self.logger = logging.getLogger(name)

        # Load config from file
        self.plugin_config = None
        self.load_config(name)

        # Set logging level after reading config
        self.logger.setLevel(logging.INFO)
        if self.plugin_config.DEBUG == 1:
            self.logger.setLevel(logging.DEBUG)

    def load_config(self, name):
        path = config.CONFIG_LOCATION
        required = name.lower() + '_config'

        # Get a list of all configuration files
        for root, dirs, files in os.walk(path):
            for filename in files:
                config_name, file_ext = os.path.splitext(filename)

                # Filter for Python files
                if  file_ext == '.py' and config_name == required:
                    package = __import__(path, fromlist = [config_name])
                    module = getattr(package, config_name)

                    self.plugin_config = module
                    return

        if self.plugin_config == None:
            self.logger.error('couldnt load configuration file')
            raise Exception()

    @abstractmethod
    def act_submission(self, submission):
        pass

    @abstractmethod
    def act_comment(self, comment):
        pass
