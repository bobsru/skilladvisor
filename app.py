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
    return render_template('home.html',
                          git_res='',
                          sof_res='', linked_res='')

@app.route('/main')
def main():
    return render_template('index.html',
                          git_res='',
                          sof_res='', linked_res='')

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

    session['github_op'] = get_user_info(github)
    #return jsonify(linkedin_data)


    #return redirect('https://stackexchange.com/oauth?client_id=5094&scope=read_inbox&redirect_uri=http://localhost:3000/stackoverflow/login/authorize')
    return render_template('stackoverflow.html')





@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')



@app.route('/stackoverflow/login/authorize',methods=['GET'])
def stackoverflow_authorized():
    # check to make sure the user authorized the request
    if not 'code' in request.args:
        return 'Access denied'

    # make a request for the access token credentials using code
    redirect_uri = url_for('stackoverflow_authorized_token', _external=True)
    data = dict(code=request.args['code'], redirect_uri=redirect_uri,client_id=5094,client_secret='vb)wKpmEN2N01lHGmW4hcw((')
    print data
    # code = request.args['code']
    # print code
    # if code is None:
    #     return 'Access denied: reason=%s error=%s' % (
    #         request.args['error'],
    #         request.args['error_description']
    #     )
    import urllib2
    url = 'https://stackexchange.com/oauth/access_token'


    http_header = {
                    "Content-type": "application/x-www-form-urlencoded"
                  }

    # params = {
    #   'client_id' : 5094,
    #   'client_secret' : 'vb)wKpmEN2N01lHGmW4hcw((',
    #   'code' : code,
    #   'redirect_uri' : 'http://localhost:3000/stackoverflow/login/authorized'
    # }
    # make a string with the request type in it:
    method = "POST"
    # create a handler. you can specify different handlers here (file uploads etc)
    # but we go for the default
    handler = urllib2.HTTPHandler()
    # create an openerdirector instance
    opener = urllib2.build_opener(handler)
    # build a request
    request2 = urllib2.Request(url, data=data )
    # add any other information you want
    request2.add_header("Content-Type",'application/x-www-form-urlencoded')
    # overload the get method function with a small anonymous function...
    request2.get_method = lambda: method
    # try it; don't forget to catch the result
    try:
        opener.open(request2)
    except urllib2.HTTPError,e:
        connection = e

    # check. Substitute with appropriate HTTP code.
    if connection.code == 200:
        data = connection.read()
        print data
    else:
        print 'Error'

    linkedin_data = session['linkedin_data']
    #return jsonify(me.data)
    #return jsonify(get_user_info(github))
    #return jsonify(linkedin_data)
    return render_template('index.html',
                           git_res=session['github_op'],
                           sof_res=session['stackof_op'], linked_res=linkedin_data)

@app.route('/stackoverflow/login/authorized',methods=['GET'])
def stackoverflow_authorized_token():
    access_token = request.args['access_token']
    if access_token is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    import requests

    url = 'https://api.stackexchange.com/2.0/me?site=stackoverflow&key=j8U2Oyj*kjXt)hyccwyhTA((&access_token=' + access_token
    r = requests.get(url)

    #return r.content
    return render_template('index.html', git_res=session['github_op'], sof_res=r.content, linked_res=session['linkedin_data'])
if __name__ == '__main__':
    app.run(host = 'localhost', port = 80)

#print get_user_info('technoweenie')
