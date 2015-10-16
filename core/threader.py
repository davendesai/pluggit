import threading

from config import config

class RedditThreader:
    """
    reddit_threader is a way to abstract the separate submission/comment
    threads out and to keep them under control. It takes care of killing
    child threads when the main process is terminated.
    """

    def __init__(self):
        # Create the necessities
        self.threads = []
        self.lock = threading.Lock()
        
    def start(self, name, target):
        thread = threading.Thread(name = name, target = target)
        thread.daemon = True

        # Start thread and keep track of it
        self.threads.append(thread)
        thread.start()

    def join(self):
        # Join all threads
        for thread in self.threads:
            thread.join()
