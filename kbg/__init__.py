# -*- coding: UTF-8 -*-

import json
import requests

API_ENDPOINT = "https://courses-api.kelbongoo.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"

BASE_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": UA,
}

__all__ = ["Kbg", "UnauthenticatedKbg"]

class UnauthenticatedKbg:
    """
    Simpler version of Kbg that exposes endpoints which don't need a logged-in
    user.
    """

    def __init__(self):
        self._token = None

    def _request_json(self, path, **kwargs):
        headers = {}
        headers.update(BASE_HEADERS)
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        kwargs.setdefault("method", "post" if "data" in kwargs else "get")
        kwargs.setdefault("url", API_ENDPOINT + path)

        if self._token:
            kwargs["headers"].setdefault("Authorization",
                    "Bearer %s" % self._token)

        r = requests.request(**kwargs)
        r.raise_for_status()
        return r.json()

    def _post_json(self, path, data):
        return self._request_json(path, data=json.dumps(data))

    def logged_in(self):
        """
        Return True if this connection has been successfully initiated.
        """
        return self._token is not None

    def get_stores(self):
        """
        Return a list of dicts representing the different stores.
        """
        # don't be confused by the name here: these are stores, not locales.
        # The website is French-only.
        return self._request_json("/locales")["locales"]


class Kbg(UnauthenticatedKbg):
    """
    Represent a connection to Kelbongoo’s website.
    """
    def __init__(self, email, password):
        self._token = None
        self._login(email, password)

    def _login(self, email, password):
        resp = self._post_json("/login", {
            "email": email,
            "password": password,
        })
        self._token = resp["token"]

    def get_consumer_information(self):
        """
        Return information about the logged-in consumer.
        """
        return self._request_json("/api/consumer")["consumer"]
