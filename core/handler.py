import logging
from time import time, sleep
from pprint import pprint

from requests import Session
from threading import Lock

class PluggitHandler:
    """
    handler is the global network handler for Pluggit. It routes all network
    requests through it in order to respect Reddit API rules. It keeps all 
    OAuth requests separate as they are based on a per-user_agent rate-limit.
    """

    def __init__(self):
        # Create logger
        self.logger = logging.getLogger('PluggitHandler')
        self.logger.setLevel(logging.DEBUG)

        # Create necessities
        self.oauth_dict = {}

        # Required by PRAW
        self.session = Session()
        self.lock = Lock()

    def __del__(self):
        if not self.session == None:
            self.session.close()

    def request(self, request, proxies, timeout, verify, **kwargs):
        pprint(vars(request))
        
