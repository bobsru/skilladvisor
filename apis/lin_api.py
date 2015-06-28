__author__ = 'shafi'

from linkedin import linkedin

API_KEY = '770rq4lgyc857p'
API_SECRET = 'jy6Yx35AiRLZGKR6'
RETURN_URL = 'http://localhost'

authentication = linkedin.LinkedInAuthentication(API_KEY, API_SECRET, RETURN_URL, ['r_basicprofile'])
# Optionally one can send custom "state" value that will be returned from OAuth server
# It can be used to track your user state or something else (it's up to you)
# Be aware that this value is sent to OAuth server AS IS - make sure to encode or hash it
#authorization.state = 'your_encoded_message'
#print authentication.authorization_url  # open this url on your browser
#application = linkedin.LinkedInApplication(authentication)


authentication.authorization_code = 'AQTm6iKRp2xz_ndANUvDnshM36BreFwknznL20jV-IJMfq19tRXEMgqeY-4SP9BwLSnv2ZCUoRbWW1uxvYdt7PqdIlW9waXaoRmDsGSjhpmy1l91c7Q&state=b6c60c9e124ee787f1229634c27fe46b'
info = authentication.get_access_token()

application = linkedin.LinkedInApplication(token=info)