__author__ = 'shafi'

from datetime import datetime
from flask import Flask, render_template,redirect, url_for, session, request, jsonify
from flask.ext.cache import Cache
from flask_oauthlib.client import OAuth
from apis.github_api import get_user_info
from apis.sof_api import get_sof_stats


global_linked = {}
sof_user_id = None
github_uname = None

app = Flask('skilladvisor')
app.debug = True
app.secret_key = 'development'
cache = Cache(app,config={'CACHE_TYPE': 'simple'})
oauth = OAuth(app)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/')
@cache.cached(60)
def webprint():
    return render_template('index.html',
                          git_res=get_user_info('technoweenie'),
                          sof_res=get_sof_stats(), linked_res='')

@app.route('/main')
def main():
    return render_template('index.html',
                          git_res=get_user_info('technoweenie'),
                          sof_res=get_sof_stats(), linked_res='')

@app.route('/users')
def list_users():
    users = {
        'shafi' : ['1537881', 'shafi-codez'],
        'technoweenie' : ['246246', 'technoweenie']
    }
    return jsonify(users)


@app.route('/users/<user_id>', methods = ['GET', 'POST', 'DELETE'])
def get_user(user_id):
    users = {
        'shafi' : ['1537881', 'shafi-codez'],
        'technoweenie' : ['246246', 'technoweenie']
    }
    if request.method == 'GET':
        if user_id in users:
            print users[user_id]
            return render_template('index.html',
                          git_res=get_user_info(users[user_id][1]),
                          sof_res=get_sof_stats(int(users[user_id][0])), linked_res='')
        else:
            return "No User Found"

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
    github_uname=request.form['git_uname']
    sof_user_id=request.form['soa_id']
    session['github'] =  github_uname
    session['stackover'] =  sof_user_id

    if 'linkedin_flag' in request.form:
        flag = request.form['linkedin_flag']
        print flag
        print global_linked
        return redirect('/linkedin')
    else:
        return render_template('index.html',
                          git_res=get_user_info(github_uname),
                          sof_res=get_sof_stats(sof_user_id), linked_res='')

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

@app.route('/api/now')
@cache.cached(50)
def current_time():
    return str(datetime.now())

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
@cache.cached()
def authorized():
    resp = linkedin.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['linkedin_token'] = (resp['access_token'], '')

    me = linkedin.get('people/~:(num-connections,picture-url,positions,location,summary,specialties,industry,headline)')

    print github_uname
    print sof_user_id
    return render_template('index.html',
                          git_res=get_user_info(session['github']),
                          sof_res=get_sof_stats(session['stackover']), linked_res=me.data)

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

if __name__ == '__main__':
    app.run(host = 'localhost', port = 3000)

#print get_user_info('technoweenie')
