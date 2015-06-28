__author__ = 'srujanabobba'

from flask import jsonify

def test(linkedin):
    me = linkedin.get('people/~?format=json')
    return me.data