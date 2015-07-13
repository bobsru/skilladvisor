__author__ = 'shafi'

from datetime import datetime
from flask import Flask, render_template,redirect, url_for, session, request, jsonify
from flask.ext.cache import Cache
from flask_oauthlib.client import OAuth
from apis.github_api import get_user_info
from apis.sof_api import get_sof_stats
import paypalrestsdk

global_linked = {}
sof_user_id = None
github_uname = None

app = Flask('skilladvisor')
app.debug = True
app.secret_key = 'development'
cache = Cache(app,config={'CACHE_TYPE': 'simple'})
oauth = OAuth(app)

paypalrestsdk.configure({
        "mode": "sandbox", # sandbox or live
        "client_id": "AXB5ZNlu09cxhnvYv4uxBhikgPhyzu_XAV1bTYwvzNKUXuNRh9RyVKA89cbCXuzHKIyhDCN5XpEthIZw",
        "client_secret": "EF8UMLBnyoKq6U3dPmFy8xaj_XFqeRncS21RnN0V-4k1cB6QFf4cmJ7c6ym79LkLZS2kiBwLk18tBs0D" })

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


# For github
github = oauth.remote_app(
    'github',
    consumer_key='0fe26cb85b62ebc2d450',
    consumer_secret='b91d81475b87c4865e01a3702998151efd84f08d',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

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
    lres = ''
    gh_res = ''
    sof_res = ''
    if 'linkedin_data' in session:
        lres = session['linkedin_data']
    if 'github_op' in session:
        gh_res = session['github_op']
    if 'sof_op' in session:
        sof_res = session['sof_op']
    return render_template('index.html',
                          git_res=gh_res,
                          sof_res=sof_res, linked_res=lres)


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


@app.route('/dashboard/', methods=['POST'])
def dashboard():
    session.clear()
    session['linkedin_data'] = ''
    session['github_op'] = ''
    session['stackof_op'] = ''

    if 'github_flag' in request.form:
        session['github_flag'] = request.form['github_flag']
    if 'stackoverflow_flag' in request.form:
        session['stackoverflow_flag'] = request.form['stackoverflow_flag']

    if 'linkedin_flag' in request.form:
        return redirect('/linkedin')
    if 'github_flag' in request.form:
        return redirect(url_for('github_index'))
    if 'stackoverflow_flag' in request.form:
        return render_template('stackoverflow.html')

    else:
        return render_template('index.html',
                          git_res='',
                          sof_res='', linked_res='')
'''
@app.route('/api/now')
@cache.cached(50)
def current_time():
    return str(datetime.now())
'''

@app.route('/linkedin')
@cache.cached(600)
def get_linkedin_resp():
    if 'linkedin_data' not in session:
        return url_for('login')
    else:
        return jsonify(session['linkedin_data'])


@app.route('/github')
@cache.cached(600)
def get_github_resp():
    if 'github_op' not in session:
        return url_for('github_login')
    else:
        return jsonify(session['github_op'])

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
    return redirect('/main', 302)

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

    session['github_op'] = get_user_info(github)
    return redirect('/main', 302)

@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')




@app.route('/payment')
def get_payment():
    # Payment
    # A Payment Resource; create one using
    # the above types and intent as 'sale'


    payment = paypalrestsdk.Payment({
        "intent": "sale",

        # Payer
        # A resource representing a Payer that funds a payment
        # Payment Method as 'paypal'
        "payer": {
            "payment_method": "paypal"},

        # Redirect URLs
        "redirect_urls": {
            "return_url": "http://localhost:80/payment/execute",
            "cancel_url": "http://localhost:80/"},

        # Transaction
        # A transaction defines the contract of a
        # payment - what is the payment for and who
        # is fulfilling it.
        "transactions": [{

            # ItemList
            "item_list": {
                "items": [{
                    "name": "Skill Advisor Pro",
                    "sku": "Pro",
                    "price": "20.00",
                    "currency": "USD",
                    "quantity": 1}]},

            # Amount
            # Let's you specify a payment amount.
            "amount": {
                "total": "20.00",
                "currency": "USD"},
            "description": "Skill Advisor Pro"}]})

    # Create Payment and return status
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        # Redirect the user to given approval url
        for link in payment.links:
            if link.method == "REDIRECT":
                # Convert to str to avoid google appengine unicode issue
                # https://github.com/paypal/rest-api-sdk-python/pull/58
                redirect_url = str(link.href)
                return redirect(redirect_url)
    else:
        print("Error while creating payment:")
        print(payment.error)

@app.route('/payment/execute')
def payment_execute():
    # ID of the payment. This ID is provided when creating payment.
    payment = paypalrestsdk.Payment.find(request.args['paymentId'])

    # PayerID is required to approve the payment.
    if payment.execute({"payer_id": request.args['PayerID']}):  # return True or False
        return "Thank you for your payment"
    else:
        print(payment.error)

# Stackoverflow oauth 2.0 from scratch
# starts
CLIENT_ID = "5094"
CLIENT_SECRET = "vb)wKpmEN2N01lHGmW4hcw(("
REDIRECT_URI = "http://localhost:5000/stack_callback"
import requests
import requests.auth



@app.route('/stack_callback')
def stack_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error

    code = request.args.get('code')

    post_data = {"client_id": CLIENT_ID,
                 "client_secret": CLIENT_SECRET,
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    response = requests.post("https://stackexchange.com/oauth/access_token", data=post_data)

    # Verify the response has access_token in it
    if 'access_token' in response.text:
        url = 'https://api.stackexchange.com/2.0/me?site=stackoverflow&key=j8U2Oyj*kjXt)hyccwyhTA((&' + response.text
        r = requests.get(url)
        import json
        session['sof_op']=json.loads(r.content)
    else:
        session['sof_op'] = 'Could not load your data. Please try again later'

    lres = ''
    gh_res = ''
    if 'linkedin_data' in session:
        lres = session['linkedin_data']
    if 'github_op' in session:
        gh_res = session['github_op']

    return render_template('index.html', git_res=gh_res, sof_res=session['sof_op'], linked_res=lres)

# Stackoverflow oauth 2.0 ends


if __name__ == '__main__':
    app.run(host = 'localhost', port = 5000)
