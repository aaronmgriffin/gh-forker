from flask import (
    redirect,
    render_template,
    request,
    Response,
    session,
    url_for
)

from app_setup import setup
from forker import GithubForker

REPO_TO_FORK = 'phrakture/gh-forker'

app, oauth = setup(__name__)

@app.route('/')
def index():
    already_forked = False
    if 'token' in session:
        forker = GithubForker(session['token']['access_token'])
        already_forked = forker.repo_exists(REPO_TO_FORK)

    return render_template(
        'index.html',
        user=session.get('user'),
        already_forked=already_forked,
        msg=request.args.get('msg')
    )


@app.route('/login')
def login():
    # Bounce to github for authentication
    return oauth.github.authorize_redirect(
        url_for('auth', _external=True)
    )


@app.route('/auth')
def auth():
    if 'error' in request.args:
        # TODO this could use a prettier error page, but at another time
        return Response(
            '\n'.join((
                f"Authentication Error: {request.args.get('error')}",
                f"Description: {request.args.get('error_description')}",
                f"See: {request.args.get('error_uri')}"
            )),
            mimetype='text/plain'
        )
    # github redirects here once authenticated
    # Now we can now get the user's access_token and other info
    session['token'] = oauth.github.authorize_access_token()
    session['user'] = oauth.github.userinfo(token=session['token'])

    return redirect('/')


@app.route('/fork')
def fork():
    msg = 'No token found, login first.'
    if 'token' in session:
        forker = GithubForker(session['token']['access_token'])
        msg = forker.fork_from(REPO_TO_FORK)

    return redirect(url_for('index', msg=msg))


@app.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
