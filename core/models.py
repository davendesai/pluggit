from abc import ABCMeta

class PluggitModel:
    """
    models contains models for converting the data taken from PRAW and the 
    reddit API to a format more palatable to the Mongo database used in 
    pluggit.
    """

    __metaclass__ = ABCMeta

    def __init__(self, obj):
        [self.create_field(key, value) for key, value in obj.__dict__.iteritems() \
         if not key[0] == '_' and not callable(value)]
        
    def create_field(self, key, value):
        if key == 'reddit_session':
            return
        # Excludes for submissions
        elif key in ['subreddit', 'author']:
            setattr(self, key, str(value))
        else:
            setattr(self, key, value)
    
class PluggitSubmission(PluggitModel):
    def __init__(self, submission):
        super(PluggitSubmission, self).__init__(submission)
        
class PluggitComment(PluggitModel):
    def __init__(self, comment):
        super(PluggitComment, self).__init__(comment)
