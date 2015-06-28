__author__ = 'shafi'

from flask import Flask, render_template,redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from apis.github_api import get_user_info
from apis.sof_api import get_sof_stats


global_linked = {}
sof_user_id = None
github_uname = None

app = Flask('skilladvisor')
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/')
def webprint():
    return render_template('index.html',
                          git_res='',
                          sof_res='', linked_res='')

@app.route('/main')
def main():
    return render_template('index.html',
                          git_res='',
                          sof_res='', linked_res='')

# Define a route for the default URL, which loads the form
@app.route('/getstats')
def form():
    #return render_template('form_submit.html')
    return render_template('register.html')

# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is
# accepting: POST requests in this case
@app.route('/dashboard/', methods=['POST'])
def dashboard():
    session['github_flag'] = request.form['github_flag']
    session['stackof_op'] = ''
    if request.form['soa_id'] != '':
        session['stackof_op'] = get_sof_stats(sof_user_id)

    if 'linkedin_flag' in request.form:
        return redirect('/linkedin')
    else:
        return render_template('index.html',
                          git_res=get_user_info(github_uname),
                          sof_res=session['stackof_op'], linked_res='')

linkedin = oauth.remote_app(
    'linkedin',
    consumer_key='770rq4lgyc857p',
    consumer_secret='jy6Yx35AiRLZGKR6',
    request_token_params={
        'scope': 'r_basicprofile',
        'state': 'RandomString',
    },
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)

@app.route('/linkedin')
def index():
    # if 'linkedin_token' in session:
    #     me = linkedin.get('people/~')
    #     return jsonify(me.data)
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return linkedin.authorize(callback=url_for('authorized', _external=True))


@app.route('/login/authorized')
def authorized():
    resp = linkedin.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['linkedin_token'] = (resp['access_token'], '')

    me = linkedin.get('people/~:(num-connections,picture-url,positions,location,summary,specialties,industry,headline)')

    session['linkedin_data'] = me.data

    if session['github_flag']:
        return redirect(url_for('github_index'))
    else:
        return render_template('index.html',git_res='',
                           sof_res=session['stackof_op'], linked_res=me.data)




@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get('linkedin_token')


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(405)
def not_allowed(error):
    return render_template('404.html'), 405

def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

linkedin.pre_request = change_linkedin_query




# For github

github = oauth.remote_app(
    'github',
    consumer_key='4d137f387a1fbe9615e4',
    consumer_secret='857f6bf754a1d4bd7f90fd1de02b5cde5c5b87f0',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

@app.route('/github')
def github_index():
    # if 'github_token' in session:
    #     me = github.get('user')
    #     return jsonify(me.data)
    return redirect(url_for('github_login'))


@app.route('/github/login')
def github_login():
    return github.authorize(callback=url_for('github_authorized', _external=True))


@app.route('/github/logout')
def github_logout():
    session.pop('github_token', None)
    return redirect(url_for('github_index'))


@app.route('/github/login/authorized')
def github_authorized():
    resp = github.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['github_token'] = (resp['access_token'], '')
    #me = github.get('user')
    linkedin_data = session['linkedin_data']
    #return jsonify(get_user_info(github))
    #return jsonify(linkedin_data)
    return render_template('index.html',
                           git_res=get_user_info(github),
                           sof_res=session['stackof_op'], linked_res=linkedin_data)


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')

if __name__ == '__main__':
    app.run(host = 'localhost', port = 3000)

#print get_user_info('technoweenie')
