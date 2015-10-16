import praw
from pprint import pprint

import config
import credentials

def main():
	r = praw.Reddit(user_agent = credentials.user_agent)

	# Later convert to using OAuth2
	r.login(credentials.bot_name, credentials.bot_password, disable_warning = True)	

        while True:
                submission = r.get_submission(submission_id = credentials.thread_id)
                comment_tree = submission.comments

                for top_level_comment in comment_tree:
                        print top_level_comment.body
                
                # Keep within Reddit API rules
                time.sleep(5)
        
if __name__ == '__main__':
        main()
