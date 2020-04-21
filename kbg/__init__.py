# -*- coding: UTF-8 -*-

import json
import requests

__version__ = "0.0.4"

API_ENDPOINT = "https://courses-api.kelbongoo.com"

BASE_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}


# Some endpoints return lists of MongoDB objects. We probably don't need the
# internal ids, so let's strip them.
def _strip_mongodb_id(x):
    """
    Rename the ``_id`` key from a dict as ``id``, if the latter doesn't already
    exist. If that's the case, remove the key.
    Update the object in-place.
    """
    if "_id" in x:
        if "id" not in x:
            x["id"] = x.pop("_id")
        else:
            del x["_id"]
    return x


def _strip_mongodb_ids(xs):
    for x in xs:
        _strip_mongodb_id(x)
    return xs


def _fix_product_fields(product):
    if "producerproduct_id" in product and "id" not in product:
        product["id"] = product.pop("producerproduct_id")
    return product

def _fix_order_fields(order):
    order = _strip_mongodb_id(order)
    order["store"] = order.pop("locale")
    order["products"] = _strip_mongodb_ids(
            [_fix_product_fields(p) for p in order.pop("items")])
    return order


class UnauthenticatedKbg:
    """
    Simpler version of ``Kbg`` that exposes endpoints which don't need a
    logged-in user.
    """

    def __init__(self):
        self._token = None
        self._store_offers = {}

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

        See ``get_store_offer`` to get all products and their ``id`` key that
        you can use in the availability ``dict``.
        """
        resp = self._request_json("/available", params={"locale": store_id})
        return resp["available"]

    def get_store_offer(self, store_id, force=False):
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
        The ``id`` key can also be used to get the product’s availability using
        ``get_store_availabilities``.
        """
        if force or store_id not in self._store_offers:
            resp = self._request_json("/init", params={"locale": store_id})
            offer = {}
            for k in ("products", "categories", "promogroups", "families",
                      "producers"):
                items = resp[k]

                if k == "products":
                    items = [_fix_product_fields(p) for p in items]

                offer[k] = _strip_mongodb_ids(items)

            self._store_offers[store_id] = offer

        return self._store_offers[store_id]

    def get_store_offer_dicts(self, store_id, force=False):
        """
        Equivalent of ``get_store_offer`` but each key is a ``dict`` mapping
        items by their id.
        """
        offer = self.get_store_offer(store_id, force=force)
        for k, items in offer.items():
            offer[k] = {item["id"]: item for item in items}

        return offer

    def get_store_status(self, store_id):
        """
        Return a ``dict`` giving details on the store's status:
         - ``"is_active"``: is it active? (e.g. we are in the timeframe for
           orders)
         - ``"is_full"``: is it full? (e.g. no orders can be taken anymore)
           - ``"full_tags"``: if full, a collection of tags describing what
             is full (possible values are ``"ORDERS"``, ``"SEC"``,
             ``"FRAIS"``).

        ``store_id`` must be the three-uppercase-letters code of the store. See
        ``get_stores`` for a list.
        """
        resp = self._request_json("/available", params={"locale": store_id})
        is_active = resp.get("globalorder", {}).get("status") == 2
        stores = resp.get("globalorderlocales", [])

        closed_tags = []
        for store in stores:
            if store["locale"] == store_id:
                closed_tags = store["closed_tags"]

        return {
            "is_active": is_active,
            "is_full": bool(closed_tags),
            "full_tags": closed_tags,
        }


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

    def get_customer_information(self):
        """
        Return information about the logged-in customer.
        """
        return self._request_json("/api/consumer")["consumer"]

    def get_customer_orders(self, page=1):
        """
        Get the logged-in customer’s orders. Return a ``dict`` with the
        following keys:
        * ``orders``
        * ``count``: total orders count.
        * ``page``: the current page, passed as an argument (min. 1).
        * ``next_page``: the next page to request, or ``None`` if it's the last
          page. This is guessed from the total count; it’s not a response from
          the API.
        """
        if page <= 0:
            # the server returns a 500 on page<=0
            page = 1

        resp = self._request_json("/api/orders/fetch-for-consumer",
                                  params={"page": page})

        orders = resp["items"]

        for order in orders:
            order = _fix_order_fields(order)

        next_page = None
        if orders:
            current_count = 10 * (page-1) + len(orders)
            if current_count < resp["count"]:
                next_page = page + 1

        return {
            "orders": orders,
            "count": resp["count"],
            "page": page,
            "next_page": next_page,
        }

    def get_all_customer_orders(self, full=False):
        """
        Generator of all the logged-in customer’s orders.
        If ``full`` is ``True``, make another call to get each order’s full
        information (see ``get_customer_orders()``).
        """
        page = 1
        while page:
            orders_resp = self.get_customer_orders(page=page)
            for order in orders_resp["orders"]:
                if full:
                    order = self.get_customer_order(order["id"])
                yield order
            page = orders_resp["next_page"]

    def get_customer_order(self, order_id):
        """
        Get more details about an order, including product names and dates when
        the order was created, retrieved, paid for.
        """
        resp = self._request_json("/api/orders/fetch-detail",
                                  # Not sure what this getPayments does
                                  params={"order_id": order_id,
                                          "getPayments": "true"})
        order = _fix_order_fields(resp["order"])
        products_infos = {}
        for product_info in order.pop("producerproducts"):
            product_info = _strip_mongodb_id(product_info)
            pid = product_info["id"]
            del product_info["id"]
            products_infos[pid] = product_info

        for product in order["products"]:
            product = _strip_mongodb_id(product)
            product.update(products_infos[product["id"]])

        return order
