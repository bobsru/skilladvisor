__author__ = 'shafi'

from stackauth import StackAuth
from stackexchange import Site, StackOverflow

global_github_json = {}

import json

global_sof_json = {}

def get_reputation(user_id=1537881):
    '''
    :param user_id:
    :return:
    '''

    #print 'StackOverflow user %d\'s accounts:' % user_id
    global_sof_json['uid'] = user_id

    stack_auth = StackAuth()
    so = Site(StackOverflow)
    accounts = stack_auth.associated(so, user_id)
    reputation = {}

    for account in accounts:
        #print '%s / %d reputation' % ( account.on_site.name, account.reputation)
        reputation[account.reputation] = account.on_site.name

    global_sof_json['reputated_on'] = reputation[max(reputation)]
    global_sof_json['reputation'] = max(reputation)
    #print 'Most reputation on: %s' % reputation[max(reputation)]

def get_accept_rate(user_id=246246):

    #print 'StackOverflow user %d\'s experience:' % user_id

    so = Site(StackOverflow)
    user = so.user(user_id)

    #print 'Total badge count : %s'% user.badge_total
    global_sof_json['badges'] = user.badge_total
    if len(user.top_answer_tags.fetch()) > 0:
        global_sof_json['experienced'] = user.top_answer_tags.fetch()[0].tag_name

    #print 'Most experienced on %s.' % user.top_answer_tags.fetch()[0].tag_name
    #print 'Most curious about %s.' % user.top_question_tags.fetch()[0].tag_name

    total_questions = len(user.questions.fetch())
    unaccepted_questions = len(user.unaccepted_questions.fetch())
    accepted = total_questions - unaccepted_questions
    rate = accepted / float(total_questions) * 100
    global_sof_json['accept_rate'] = format(rate, '.2f')
    #print 'Accept rate is %.2f%%.' % rate

def get_sof_stats(user_id=246246):
    get_reputation(user_id)
    get_accept_rate(user_id)
    return global_sof_json

#print json.dumps(get_sof_stats(),indent=4)