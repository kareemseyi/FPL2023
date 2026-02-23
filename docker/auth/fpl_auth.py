import logging
import os
import uuid
import re
import utils
from constants import endpoints
from dataModel.user import User

logger = logging.getLogger(__name__)


LOGIN_URL = endpoints["API"]["LOGIN"]
AUTH_URL = endpoints["API"]["AUTH"]
API_ME = endpoints["API"]["ME"]
REDIRECT_URI = endpoints["API"]["REDIRECT_URI"]
DAVINCI_POLICY_START_URL = endpoints["API"]["DAVINCI_POLICY_START"]
DAVINCI_CONNECTIONS_URL = endpoints["API"]["DAVINCI_CONNECTIONS"]
AS_RESUME_URL = endpoints["API"]["AS_RESUME"]
AS_TOKEN_URL = endpoints["API"]["AS_TOKEN"]
STANDARD_CONNECTION_ID = "867ed4363b2bc21c860085ad2baa817d"


class FPLAuth:
    """Handles FPL authentication and access token"""

    def __init__(self, session):
        self.session = session
        self.user = None

    async def login(self, email=None, password=None):
        """Returns a requests session with FPL login authentication.

        Args:
            email: Email address for the user's FPL account.
            password: Password for the user's FPL account.
        """
        email, password = self._resolve_credentials(email, password)
        logger.info("Logging in: %s", LOGIN_URL)

        code_verifier = utils.generate_code_verifier()
        code_challenge = utils.generate_code_challenge(code_verifier)

        access_token, new_state = await self._authorize(code_challenge)
        auth_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        dv_response = await self._davinci_flow(auth_headers, email, password)

        auth_code = await self._get_auth_code(dv_response, new_state)
        await self._exchange_token(auth_code, code_verifier)
        return self.session

    @staticmethod
    def _resolve_credentials(email, password):
        """Resolves credentials from args, Secret Manager, or env vars."""
        if not email and not password:
            email, password = utils.get_credentials_from_secret_manager()
            if not email or not password:
                email = os.getenv("FPL_EMAIL")
                password = os.getenv("FPL_PASSWORD")
        if not email or not password:
            raise ValueError(
                "Email and password must be set. Configure them in "
                "Google Secret Manager or environment variables."
            )
        return email, password

    async def _authorize(self, code_challenge):
        """Initiates OAuth2 authorize and returns access token + state."""
        params = {
            "response_type": "code",
            "scope": "openid profile email offline_access",
            "client_id": "bfcbaf69-aade-4c1b-8f00-c1cb8a193030",
            "redirect_uri": REDIRECT_URI,
            "state": uuid.uuid4().hex,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        async with self.session.get(AUTH_URL, params=params) as response:
            assert response.status == 200
            text = await response.text()
            access_token = re.search(r'"accessToken":"([^"]+)"', text).group(1)
            new_state = re.search(
                r'<input[^>]+name="state"[^>]+value="([^"]+)"', text
            ).group(1)
            logger.info("Successfully Retrieved Access Token... Continuing...")
            return access_token, new_state

    async def _davinci_flow(self, auth_headers, email, password):
        """Runs the DaVinci policy flow and returns the dvResponse."""
        async with self.session.post(
            DAVINCI_POLICY_START_URL, headers=auth_headers
        ) as response:
            assert response.status == 200
            response = await response.json()
            interaction_id = response["interactionId"]

        # Polling step
        async with self.session.post(
            DAVINCI_CONNECTIONS_URL.format(STANDARD_CONNECTION_ID),
            headers={"interactionId": interaction_id},
            json={
                "id": response["id"],
                "eventName": "continue",
                "parameters": {"eventType": "polling"},
                "pollProps": {
                    "status": "continue",
                    "delayInMs": 10,
                    "retriesAllowed": 1,
                    "pollChallengeStatus": False,
                },
            },
        ) as response:
            assert response.status == 200
            response = await response.json()

        # Submit credentials
        async with self.session.post(
            DAVINCI_CONNECTIONS_URL.format(STANDARD_CONNECTION_ID),
            headers={"interactionId": interaction_id},
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
            },
        ) as response:
            assert response.status == 200
            response = await response.json()

        # Confirm sign-on
        async with self.session.post(
            DAVINCI_CONNECTIONS_URL.format(response["connectionId"]),
            headers=auth_headers,
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
            logger.info("DaVinci flow completed, interactionToken received")
            return response["dvResponse"]

    async def _get_auth_code(self, dv_response, state):
        """Resumes the auth session and extracts the authorization code."""
        async with self.session.post(
            AS_RESUME_URL,
            data={"dvResponse": dv_response, "state": state},
            allow_redirects=False,
        ) as response:
            assert response.status in (200, 302)
            location = response.headers["Location"]
            return re.search(r"[?&]code=([^&]+)", location).group(1)

    async def _exchange_token(self, auth_code, code_verifier):
        """Exchanges authorization code for access token and sets user."""
        async with self.session.post(
            AS_TOKEN_URL,
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
            access_token = response["access_token"]
            user = await utils.fetch(
                self.session, API_ME, headers=utils.headers_access(access_token)
            )
            self.user = User(user, self.session, access_token)
