import os
import sys

from flask import Flask
from authlib.integrations.flask_client import OAuth


# This method is taken direct from authlib/loginpass for sanitizing github user info
def normalize_userinfo(client, data):
    params = {
        'sub': str(data['id']),
        'name': data['name'],
        'email': data.get('email'),
        'preferred_username': data['login'],
        'profile': data['html_url'],
        'picture': data['avatar_url'],
        'website': data.get('blog'),
    }

    # The email can be be None despite the scope being 'user:email'.
    # That is because a user can choose to make his/her email private.
    # If that is the case we get all the users emails regardless if private or note
    # and use the one he/she has marked as `primary`
    if params.get('email') is None:
        resp = client.get('user/emails')
        resp.raise_for_status()
        data = resp.json()
        params["email"] = next(email['email'] for email in data if email['primary'])
    return params


def getenv(name):
    envvar = os.getenv(name)
    if not envvar:
        msg = "Configuration Error: no '%s' environment variable found" % name
        sys.stderr.write(msg + '\n')
        raise RuntimeError(msg)
    return envvar


def setup(name):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=getenv('SESSION_KEY'),
        GITHUB_CLIENT_ID=getenv('GITHUB_CLIENT_ID'),
        GITHUB_CLIENT_SECRET=getenv('GITHUB_CLIENT_SECRET')
    )

    oauth = OAuth(app)
    oauth.register(
        name='github',
        api_base_url='https://api.github.com/',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        client_kwargs={'scope': 'read:user user:email public_repo'},
        userinfo_endpoint='https://api.github.com/user',
        userinfo_compliance_fix=normalize_userinfo,
    )

    return app, oauth

