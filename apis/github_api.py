__author__ = 'srujanabobba'

import urllib2
import json

global_github_json = {}

def get_user_info(github):
    try:
        #r_data = urllib2.urlopen('https://api.github.com/users/' + username).read()
        r_data = github.get('user')
        data = r_data.data

        #print data['followers']
        global_github_json['followers'] = data['followers']
        global_github_json['user_created_on'] = data['created_at']

        # Get the repos count
        #print data['repos_url']
        r_repos = github.get('user/repos')
        repos_data = r_repos.data

        #repos = urllib2.urlopen(data['repos_url']).read()
        #return repos
        global_github_json['repos_count'] = len(repos_data)

        # Get the languages used,stars and watchers count

        languages_used = []
        stargazers_total_count = 0
        watchers_total_count = 0
        for repo in repos_data:
            if repo['language'] not in languages_used and repo['language'] is not None:
                languages_used.append(repo['language'])

            stargazers_total_count += repo['stargazers_count']
            watchers_total_count += repo['watchers_count']

        global_github_json['languages_used'] = languages_used
        global_github_json['stargazers_total_count'] = stargazers_total_count
        global_github_json['watchers_total_count'] = watchers_total_count
    except:
        pass
    return global_github_json

#print json.dumps(get_user_info('technoweenie'),indent=4)