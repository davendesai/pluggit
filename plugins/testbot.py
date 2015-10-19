from core.plugin import RedditPlugin

class TestBot(RedditPlugin):

    def __init__(self):
        super(TestBot, self).__init__('TestBot')

    def act_submission(self, submission):
        pass
    
    def act_comment(self, comment):
        pass
        
def init():
    return TestBot()
