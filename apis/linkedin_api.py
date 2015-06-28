__author__ = 'srujanabobba'

from flask import jsonify

def test(linkedin):
    try:
        #return 'test'
        me = linkedin.get('people/~')
        #return me
        #if me:
        #    return me.data
        return {}
    except:
        pass
