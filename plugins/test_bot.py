from core.plugin import RedditPlugin

class TestBot(RedditPlugin):

    def __init__(self, handler):
        super(TestBot, self).__init__('TestBot', handler)

    def act_submission(self, submission):
        self.logger.debug('SUBMISSION: ' + submission.body)
    
    def act_comment(self, comment):
        self.logger.debug('COMMENT: ' + comment.body)

def init(handler):
    return TestBot(handler)
