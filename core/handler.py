from time import time, sleep

from requests import Session
from threading import Lock

class PluggitHandler:
    """
    handler is the global network handler for Pluggit. It routes all network
    requests through it in order to respect Reddit API rules. It keeps all 
    OAuth requests separate as they are based on a per-user_agent rate-limit.
    """

    def __init__(self):
        # Create dict { bearer: last_request_time }
        self.oauth_dict = {}

        # Required by PRAW
        self.session = Session()
        self.lock = Lock()

    def __del__(self):
        if not self.session == None:
            self.session.close()

    def request(self, request, proxies, timeout, verify, **kwargs):
        # Evict oauth_session if more than 1hr old
        self.oauth_dict = { key:value for key, value in self.oauth_dict.items() if value < (time() + (60 * 60)) }

        # Get current oauth_session
        oauth_session = None
        if 'Authorization' in request.headers:
            payload = request.headers['Authorization'].split(' ')

            if payload[0] == 'bearer':
                oauth_session = payload[1]
                
        if not oauth_session == None:
            # Previously made a request
            if oauth_session in self.oauth_dict:
                # Lock to prevent multiple threads requesting from same OAUTH session
                with self.lock:
                    now = time()
                    wait_time = self.oauth_dict[oauth_session] + 1 - now

                    if wait_time > 0:
                        print 'have to sleep: ' + str(wait_time)
                        now += wait_time
                        sleep(wait_time)
                        
                    self.oauth_dict[oauth_session] = now
                
            else:
                self.oauth_dict[oauth_session] = time()
     
        return self.session.send(request,
                                 proxies = proxies,
                                 timeout = timeout,
                                 allow_redirects = False, verify = verify)
