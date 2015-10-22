import os
import logging
import mongoengine

class PluggitDatabase:
    """
    database is the single store for all plugins using Pluggit. It provides a
    central place to store the ids that were processed during uptime. It allows
    for Pluggit to work regardless of network or system fluctuations.
    """

    def __init__(self, name):
        # Create logger
        self.logger = logging.getLogger('PluggitDatabase')
        self.logger.setLevel(logging.INFO)
        
        hostpath = 'mongodb://127.0.0.1:27015'
        try:
            #mongoengine.connect(name, host = os.environ['MONGOLAB_URI'])
            mongoengine.connect(name, host = hostpath)
        except Exception as e:
            self.logger.error('unable to connect to the database')
            raise
        
