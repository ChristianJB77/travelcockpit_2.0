# Libraries
from functools import wraps
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv
from authlib.integrations.flask_client import OAuth
from jose import jwt
from urllib.request import urlopen
from flask import request, _request_ctx_stack, abort, session
import json
import os
# Constants for Auth0 from constants.py, stores temporary config variables
import auth.constants as constants


"""Auth0 variables"""


# Get Auth0 environment varibales from .env file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Auth0 varibales
AUTH0_CALLBACK_URL = os.environ['AUTH0_CALLBACK_URL']
AUTH0_CLIENT_ID = os.environ['AUTH0_CLIENT_ID']
AUTH0_CLIENT_SECRET = os.environ['AUTH0_CLIENT_SECRET']
AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = os.environ['AUTH0_AUDIENCE']
AUTH0_ALGORITHMS = os.environ['AUTH0_ALGORITHMS']


"""AuthError Exception - A standardized way to communicate auth failure modes"""


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


"""Register and authentificate Auth0"""

def auther(app):

    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        api_base_url=AUTH0_BASE_URL,
        access_token_url=AUTH0_BASE_URL + '/oauth/token',
        authorize_url=AUTH0_BASE_URL + '/authorize',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )
    auth0_dict = {"auth0" : auth0,
                    "url" : AUTH0_CALLBACK_URL,
                    "audi" : AUTH0_AUDIENCE,
                    "id" : AUTH0_CLIENT_ID}

    return auth0_dict


# API permission must be in JWT
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permission NOT included in JWT!'
        }, 400)
    # If permission is empty, then no user is not authorized
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Forbidden access (permission NOT found)'
        }, 403)


def verify_decode_jwt(token):
    # Get Json Web Key Set -> Public key of asymmetric signature
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    # Get data in token header of current session/user -> Private key
    unverified_header = jwt.get_unverified_header(token)
    # Check if token has kid key
    if "kid" not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization NOT correctly formatted!'
        }, 401)

    # Get RSA Key
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    # Validate key
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=AUTH0_ALGORITHMS,
                audience=AUTH0_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired!'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims, check the audience & issuer!'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token!'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key!'
    }, 400)


"""RBAC splitter"""


# Authenticate JWT (WITHOUT RBAC permission)
def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = session[constants.ACCESS_TOKEN]
        payload = verify_decode_jwt(token)

        return f(payload, *args, **kwargs)
    return wrapper


#Authenticate JWT WITH RBAC permission
def requires_auth_rbac(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = session[constants.ACCESS_TOKEN]
            payload = verify_decode_jwt(token)

            check_permissions(permission, payload)

            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
