import http

from api.handler import fetch, get_current_gameweek, logged_in
from endpoints import endpoints
import aiohttp
from http import cookies


API_BASE_URL = endpoints["API"]["BASE_URL"]
LOGIN_URL = endpoints["API"]["LOGIN"]
import os
class FPL():
    """The FPL class."""

    def __init__(self, session):
        self.session = session

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
        # await self.session.get(API_BASE_URL)
        # filtered = self.session.cookie_jar.filter_cookies(API_BASE_URL)
        # print(filtered)
        # assert filtered["csrftoken"]
        # csrf_token = filtered["csrftoken"].value
        headers = {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1; PRO 5 Build/LMY47D)", 'accept-language': 'en'}
        cookies = http.cookies.SimpleCookie()
        payload = {

            "login": email,
            "password": password,
            "app": "plfpl-web",
            "redirect_uri": "https://fantasy.premierleague.com/a/login",
            "Set-Cookie": cookies

        }
        async with self.session.post(LOGIN_URL, data=payload, headers=headers, cookies=cookies) as response:
            assert response.status == 200
            if "state=success" in str(response.url):
                # filtered = response.headers
                # csrf_token = filtered["csrftoken"].value
                print("Successfully logged In")
            else:
                # response = await response
                if "state=fail" in str(response.url):
                    raise ValueError("Incorrect email or password!")