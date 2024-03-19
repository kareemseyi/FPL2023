import http
import aiohttp
import os
from endpoints import endpoints
from http import cookies
from utils import fetch
from dataModel.user import User


API_MY_TEAM_GW_URL = endpoints['API']['MY_TEAM_GW']
API_BASE_URL = endpoints["API"]["BASE_URL"]
API_ME = endpoints['API']['ME']
LOGIN_URL = endpoints["API"]["LOGIN"]


async def get_current_user(session):
    print('getting current')
    user = await fetch(session, API_ME)
    return user


class FPL:
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

    def logged_in(self):
        """Checks that the user is logged in within the session.


        :return: True if user is logged in else False
        :rtype: bool
        """
        return "csrftoken" in self.session.cookie_jar.filter_cookies(
            "https://users.premierleague.com/")

    async def get_user(self, user_id=None, return_json=False):
        """Returns the user with the given ``user_id``.

        Information is taken from e.g.:
            https://fantasy.premierleague.com/api/entry/91928/

        :param session:
        :param user_id: A user's ID.
        :type user_id: string or int
        :param return_json: (optional) Boolean. If ``True`` returns a ``dict``,
            if ``False`` returns a :class:`User` object. Defaults to ``False``.
        :type return_json: bool
        :rtype: :class:`User` or `dict`
        """
        if user_id:
            assert int(user_id) > 0, "User ID must be a positive number."
        else:
            # If no user ID provided get it from current session
            try:
                user = await get_current_user(self.session)
                user_id = user["player"]["entry"]
            except TypeError:
                raise Exception("You must log in before using `get_user` if "
                                "you do not provide a user ID.")

        url = API_ME.format(user_id)
        user = await fetch(self.session, url)

        if return_json:
            return user
        return User(user, self.session)

    async def get_users_team(self, user, gw):
        """Returns a logged-in user's current team. Requires the user to have
        logged in using ``fpl.login()``.

        :rtype: list
        """
        if not FPL.logged_in(self):
            raise Exception("User must be logged in.")

        try:
            response = await fetch(
                self.session, API_MY_TEAM_GW_URL.format(f=user.entry, gw=gw))
        except Exception as e:
            raise Exception("Client has not set a team for gameweek " + str(gw))
        return response['picks']

