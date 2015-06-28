__author__ = 'shafi'

from flask import Flask, render_template,redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from apis.github_api import get_user_info
from apis.sof_api import get_sof_stats


global_linked = {}

app = Flask('skilladvisor')
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

@app.route('/')
def webprint():
    return render_template('index.html',
                          git_res=get_user_info('technoweenie'),
                          sof_res=get_sof_stats(), linked_res='')

# Define a route for the default URL, which loads the form
@app.route('/form')
def form():
    return render_template('form_submit.html')

# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is
# accepting: POST requests in this case
@app.route('/hello/', methods=['POST'])
def hello():
    name=request.form['git_uname']
    email=request.form['soa_id']
    if 'linkedin_flag' in request.form:
        flag = request.form['linkedin_flag']
        print flag
        print global_linked
        return redirect('/linkedin')

        jsonify(global_linked)
        #return render_template('form_action.html', name=name, email=email, val = flag)
    else:
        return render_template('form_action.html', name=name, email=email, val = 'False')

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

    return render_template('index.html',
                          git_res=get_user_info('technoweenie'),
                          sof_res=get_sof_stats(), linked_res=me.data)

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
