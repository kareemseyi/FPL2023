import http

from api.handler import fetch, logged_in
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
            email = os.getenv("FPL_EMAIL", 'kareemseyi@gmail.com')
            password = os.getenv("FPL_PASSWORD", '@oek917K')
        if not email or not password:
            raise ValueError("Email and password must be set")
        print(f"Logging in: {LOGIN_URL}")
        print(f"Logging in: {email}, {password}")

        headers = {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1; PRO 5 Build/LMY47D)",
                   'accept-language': 'en'
                   }
        cookies = http.cookies.SimpleCookie()
        payload = {
            "login": email,
            "password": password,
            "app": "plfpl-web",
            "redirect_uri": "https://fantasy.premierleague.com/a/login",
            "Set-Cookie": cookies
        }
        async with self.session.post(LOGIN_URL, data=payload, headers=headers, cookies=cookies) as response:
            print(response)
            assert response.status == 200
            if "state=success" in str(response.url):
                print("Successfully logged In")
            else:
                if "state=fail" in str(response.url):
                    raise ValueError("Incorrect email or password!")
        return self.session

    def get_Fixtures(self, gameweek: int, password=None):
        if logged_in(self.session):
            print(True)

