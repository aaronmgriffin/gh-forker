import os
import sys

from authlib.integrations.flask_client import OAuth
from loginpass.github import GitHub as github_login
from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    session,
    url_for
)

THIS_REPO = 'phrakture/gh-forker'

def env_or_death(name):
    envvar = os.getenv(name)
    if not envvar:
        msg = "Configuration Error: no '%s' environment variable found" % name
        sys.stderr.writeln(msg)
        raise RuntimeError(msg)
    return envvar

app = Flask(__name__)
app.secret_key = env_or_death('SESSION_KEY')
app.config['GITHUB_CLIENT_ID'] = env_or_death('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = env_or_death('GITHUB_CLIENT_SECRET')

oauth = OAuth(app)
# using loginpass for DRY
oauth.register(name='github', **github_login.OAUTH_CONFIG)


@app.route('/')
def index():
    return render_template(
        'index.html',
        user=session.get('user')
    )


@app.route('/login')
def login():
    return oauth.github.authorize_redirect(
        url_for('auth', _external=True)
    )


@app.route('/auth')
def auth():
    session['user'] = oauth.github.parse_id_token(
        oauth.github.authorize_access_token()
    )
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
