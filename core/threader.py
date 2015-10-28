import threading
import logging

class PluggitThreader:
    """
    reddit_threader is a way to abstract the separate submission/comment
    threads out and to keep them under control. It takes care of killing
    child threads when the main process is terminated.
    """

    def __init__(self):
        self.threads = []

    def run_thread(self, target):
        thread = threading.Thread(target = target)
        thread.daemon = True

        # Start thread and keep track of it
        self.threads.append(thread)
        thread.start()

    def join_all(self):
        [thread.join() for thread in self.threads]
