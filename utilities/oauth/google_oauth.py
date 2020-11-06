import cachecontrol
import google.auth.transport.requests
import requests

from dataclasses import dataclass
from google.oauth2 import id_token
from sanic.response import json
from sanic.exceptions import Unauthorized

from springboard import Springboard
from utilities.oauth.google_oauth_database_manager import \
    GoogleOauthDatabaseManager
from utilities.validate_params import validate_required_params


@dataclass
class OAuthUser:
    user_id: str
    user_nickname: str
    user_photo: str


class GoogleOauthHandler:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self._db_manager = GoogleOauthDatabaseManager()

    def connect_springboard(self, app: Springboard):
        app.sanic.add_route(self._sign_in_with_token, 'api/g-oauth')

    async def _sign_in_with_token(self, request):
        args = validate_required_params(request.args, 'idtoken')

        token = args['idtoken'][0].replace("'", "").replace('"', '')

        try:
            session = requests.session()
            cached_session = cachecontrol.CacheControl(session)
            request = google.auth.transport.requests.Request(
                session=cached_session)
            id_info = id_token.verify_oauth2_token(token, request,
                                                   self.client_id)

            if id_info['iss'] not in ['accounts.google.com',
                                      'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            user_id = id_info['sub']
            user_nickname = id_info['name']
            user_photo = str(id_info['picture']).replace('=s96-c', '')

            session_token = self._db_manager.sign_in_or_create_oauth_user(
                user_id, user_nickname, user_photo)

            response = json({'session_token', session_token})
            response.cookies['session_token'] = session_token
            return response

        except ValueError:
            raise Unauthorized('Token not accepted')
            pass
