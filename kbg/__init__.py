# -*- coding: UTF-8 -*-

import json
import requests

__version__ = "0.0.1"

API_ENDPOINT = "https://courses-api.kelbongoo.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"

BASE_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": UA,
}

def _strip_mongodb_ids(xs):
    # Some endpoints return lists of MongoDB objects. We probably don't need
    # the internal ids, so let's strip them.
    for x in xs:
        if "_id" in x:
            del x["_id"]
    return xs

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

    def get_store_availabilities(self, store_id):
        """
        Return a ``dict`` mapping product ids to their availabilities for
        the current command window in the given store.

        ``store_id`` must be the three-uppercase-letters code of the store. See
        ``get_stores`` for a list.

        See ``get_store_offer`` to get all products and their
        ``producerproduct_id`` key that you can use in the availability
        ``dict``.
        """
        resp = self._request_json("/available", params={"locale": store_id})
        return resp["available"]

    def get_store_offer(self, store_id):
        """
        Return the current offer in the given store. The returned value is a
        ``dict`` with the following keys:

        * ``products``: products.
        * ``categories``: product categories.
        * ``families``: product families (subcategories).
        * ``producers``: producers.
        * ``promogroups``

        One can join these keys together: products have a ``producer_id`` key
        and producers have an ``id`` key. Products also refer to their family;
        families to their category, etc.
        The ``producerproduct_id`` key can also be used to get the product’s
        availability using ``get_store_availabilities``.
        """
        resp = self._request_json("/init", params={"locale": store_id})

        return {k: _strip_mongodb_ids(resp[k])
                for k in ("products", "categories", "promogroups", "families",
                    "producers")}


class Kbg(UnauthenticatedKbg):
    """
    Represent a connection to Kelbongoo’s website.
    """
    def __init__(self, email, password):
        super().__init__()
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
