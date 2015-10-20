from core.plugin import PluggitPlugin

class TestBot(PluggitPlugin):

    def __init__(self, handler):
        super(TestBot, self).__init__('TestBot', handler)

    def act_submission(self, submission):
        pass
    
    def act_comment(self, comment):
        pass
        
def init(handler):
    return TestBot(handler)
