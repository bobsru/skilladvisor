__author__ = 'shafi'

from flask import Flask, render_template
from apis.github_api import get_user_info

app = Flask('skilladvisor')

@app.route('/')
def webprint():
    cnt = get_user_info('technoweenie')
    return render_template('index.html', res=cnt['watchers_total_count'])

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 3000)

#print get_user_info('technoweenie')