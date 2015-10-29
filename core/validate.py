"""
validate is a set of definitions for validating files related to 
the Pluggit project. It provides a central place to make changes
rapidly to the necessary configurations files.
"""

def pluggit_config(options):
    # Check required options
    pass

def plugin_config(options):
    # Check required options
    assert 'user_agent' in options, 'unable to find user agent in config'
    assert 'submission_subreddits' in options, 'unable to find submission_subreddits in config'
    assert 'comment_subreddits' in options, 'unable to find comment_subreddits in config'
    assert 'scope' in options, 'unable to find scope in config'
    assert 'refreshable' in options, 'unable to find oauth refresh setting in config'
    assert 'app_key' in options, 'unable to find app_key in config'
    assert 'app_secret' in options, 'unable to find app_secret in config'
