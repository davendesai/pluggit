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

        # Create logger
        self.logger = logging.getLogger('PluggitThreader')
        self.logger.setLevel(logging.INFO)

        # Keep track of currently monitored
        self.submission_subreddits = []
        self.comment_subreddits = []

    def thread_exists(self, subreddit, submission = True, comment = True):
        if submission:
            if subreddit not in self.submission_subreddits:
                self.submission_subreddits.append(subreddit)
                self.logger.info('creating submission thread for {}'.format(subreddit))
                return False

        if comment:
            if subreddit not in self.comment_subreddits:
                self.logger.info('creating comment thread for {}'.format(subreddit))
                self.comment_subreddits.append(subreddit)
                return False
            
        return True

    def run_thread(self, name, target, argument):
        thread = threading.Thread(name = name, target = target, args = (argument,))
        thread.daemon = True

        # Start thread and keep track of it
        self.threads.append(thread)
        thread.start()

    def join_all_threads(self):
        # Join all threads
        for thread in self.threads:
            thread.join()
