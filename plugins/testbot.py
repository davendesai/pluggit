from core.plugin import PluggitPlugin

class TestBot(PluggitPlugin):

    def __init__(self, handler, database):
        super(TestBot, self).__init__('TestBot', handler, database)

    def received_submission(self, submission):
        pass
    
    def received_comment(self, comment):
        pass
        
def init(handler, database):
    return TestBot(handler, database)
