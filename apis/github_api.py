__author__ = 'srujanabobba'

import urllib2
import json

global_github_json = {}
def get_user_info(username):
    r_data = urllib2.urlopen('https://api.github.com/users/' + username).read()

    data = json.loads((r_data))
    global_github_json['followers'] = data['followers']
    global_github_json['user_created_on'] = data['created_at']

    # Get the repos count
    repos = json.loads(urllib2.urlopen(data['repos_url']).read())
    global_github_json['repos_count'] = len(repos)

    # Get the languages used,stars and watchers count

    languages_used = []
    stargazers_total_count = 0
    watchers_total_count = 0
    for repo in repos:
        if repo['language'] not in languages_used:
            languages_used.append(repo['language'])

        stargazers_total_count += repo['stargazers_count']
        watchers_total_count += repo['watchers_count']

    global_github_json['languages_used'] = languages_used
    global_github_json['stargazers_total_count'] = stargazers_total_count
    global_github_json['watchers_total_count'] = watchers_total_count
    return global_github_json

#get_user_info('technoweenie')
#print json.dumps(global_github_json,indent=4)
