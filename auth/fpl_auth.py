import os
import base64
import uuid
import re
import utils
from endpoints import endpoints
from .auth_exceptions import AuthenticationError, LoginError

LOGIN_URL = endpoints["API"]["LOGIN"]
AUTH_URL = endpoints["API"]["AUTH"]
API_ME = endpoints['API']['ME']
REDIRECT_URI = endpoints['API']['REDIRECT_URI']
DAVINCI_POLICY_START_URL = endpoints['API']['DAVINCI_POLICY_START']
DAVINCI_CONNECTIONS_URL = endpoints['API']['DAVINCI_CONNECTIONS']
AS_RESUME_URL = endpoints['API']['AS_RESUME']
AS_TOKEN_URL = endpoints['API']['AS_TOKEN']
STANDARD_CONNECTION_ID = "0d8c928e4970386733ce110b9dda8412"


class FPLAuth:
    """Handles FPL authentication and access token"""

    def __init__(self, session):
        self.session = session
        self.access_token = None

    async def login(self, email=None, password=None):
        """Returns a requests session with FPL login authentication.

        :param string email: Email address for the user's Fantasy Premier League
            account.
        :param string password: Password for the user's Fantasy Premier League
            account.
        """
        if not email and not password:
            email = os.getenv("FPL_EMAIL", 'okareem@stellaralgo.com')
            password = os.getenv("FPL_PASSWORD", '@Testing123')
        if not email or not password:
            raise ValueError("Email and password must be set")
        print(f"Logging in: {LOGIN_URL}")
        print(f"Logging in: {email}, {password}")

        code_verifier = utils.generate_code_verifier()
        code_challenge = utils.generate_code_challenge(code_verifier)

        initial_state = uuid.uuid4().hex

        params = {
            "response_type": "code",
            "scope": "openid profile email offline_access",
            "client_id": "bfcbaf69-aade-4c1b-8f00-c1cb8a193030",
            "redirect_uri": REDIRECT_URI,
            "state": initial_state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }

        async with self.session.get(AUTH_URL, params=params) as response:
            assert response.status == 200
            if response.status == 200:
                text2 = await response.text()
                access_token = re.search(r'"accessToken":"([^"]+)"', text2).group(1)
                new_state = re.search(r'<input[^>]+name="state"[^>]+value="([^"]+)"', text2).group(1)

                print('sc: ', access_token)
                print("Successfully Retrieved Access Token... Continuing...")
            else:
                if response.status != 200:
                    raise LoginError("Incorrect email or password!")

        new_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        async with self.session.post(DAVINCI_POLICY_START_URL,
                                     headers=new_headers) as response:
            assert response.status == 200
            response = await response.json()
            interaction_id = response["interactionId"]
            interaction_token = response["interactionToken"]

        print('id: ', interaction_id)
        print('it: ', interaction_token)

        async with self.session.post('DAVINCI_CONNECTIONS_URL'.format(STANDARD_CONNECTION_ID),
            headers={
                "interactionId": interaction_id,
                "interactionToken": interaction_token,
            },
            json={
                "id": response["id"],
                "eventName": "continue",
                "parameters": {"eventType": "polling"},
                "pollProps": {"status": "continue", "delayInMs": 10, "retriesAllowed": 1, "pollChallengeStatus": False},
            },
        ) as response:
            assert response.status == 200
            response = await response.json()
            print('first post complete', interaction_token)

        async with self.session.post('DAVINCI_CONNECTIONS_URL'.format(STANDARD_CONNECTION_ID),
            headers={
                "interactionId": interaction_id,
                "interactionToken": interaction_token,
            },
            json={
                "id": response["id"],
                "nextEvent": {
                    "constructType": "skEvent",
                    "eventName": "continue",
                    "params": [],
                    "eventType": "post",
                    "postProcess": {},
                },
                "parameters": {
                    "buttonType": "form-submit",
                    "buttonValue": "SIGNON",
                    "username": email,
                    "password": password,
                },
                "eventName": "continue",
            }
        ) as response:
            assert response.status == 200
            response = await response.json()
            print('second post complete', interaction_token)

        async with self.session.post('DAVINCI_CONNECTIONS_URL'.format(response["connectionId"]),
            headers=new_headers,
            json={
                "id": response["id"],
                "nextEvent": {
                    "constructType": "skEvent",
                    "eventName": "continue",
                    "params": [],
                    "eventType": "post",
                    "postProcess": {},
                },
                "parameters": {
                    "buttonType": "form-submit",
                    "buttonValue": "SIGNON",
                },
                "eventName": "continue",
            },
        ) as response:
            assert response.status == 200
            response = await response.json()
            print('third post complete', interaction_token)

        async with self.session.post(AS_RESUME_URL,
            data={
                "dvResponse": response["dvResponse"],
                "state": new_state,
            },
            allow_redirects=False,
        ) as response:
            assert response.status in (200, 302)

            location = response.headers["Location"]
            auth_code = re.search(r"[?&]code=([^&]+)", location).group(1)
            print('auth_code: ', auth_code)
            print('location: ', location)

        async with self.session.post(AS_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
                "code": auth_code,
                "code_verifier": code_verifier,
                "client_id": "bfcbaf69-aade-4c1b-8f00-c1cb8a193030",
            },
        ) as response:
             assert response.status == 200
             response = await response.json()
             self.access_token = response["access_token"]
             print('access token: ', access_token)

        return self.session

    def logged_in(self):
        """Checks that the user is logged in within the session.

        :return: True if user is logged in else False
        :rtype: bool
        """
        assert all(x in self.session.cookie_jar.filter_cookies(
            "https://account.premierleague.com/") for x in ["interactionToken", "interactionId"]), \
            "Must Be logged in"
        return True

    async def get_current_user(self):
        """Returns the current authenticated user."""
        user = await utils.fetch(self.session, API_ME, headers=utils.headers_access(self.access_token))
        return user