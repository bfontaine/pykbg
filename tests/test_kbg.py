# -*- coding: UTF-8 -*-

import responses
import unittest
import kbg as k

class TestUnauthenticatedKbg(unittest.TestCase):
    def setUp(self):
        with responses.RequestsMock() as resps:
            self.k = k.UnauthenticatedKbg()
            self.assertEqual(0, len(resps.calls))

    @responses.activate
    def test_logged_in(self):
        self.assertFalse(self.k.logged_in())

    def test_get_stores(self):
        stores = {"locales": [{"code": "ABC"}, {"code": "DEF"}]}
        with responses.RequestsMock() as resps:
            resps.add(responses.GET, k.API_ENDPOINT + "/locales",
                    json={"locales": stores})
            got_stores = self.k.get_stores()
        self.assertEqual(stores, got_stores)

    def test_get_store_availabilities(self):
        store = "XYZ"
        availabilities = {"id1": 1, "id2": 3, "id3": 2000, "id4": 0}

        with responses.RequestsMock() as resps:
            resps.add(responses.GET, k.API_ENDPOINT + "/available",
                    json={"available": availabilities})
            got_availabilities = self.k.get_store_availabilities(store)
            self.assertEqual(1, len(resps.calls))
            self.assertRegexpMatches(resps.calls[0].request.url,
                    r"\?locale=%s$" % store)

        self.assertEqual(availabilities, got_availabilities)


class TestKbg(unittest.TestCase):
    def setUp(self):
        self.email = "yo@example.com"
        self.password = "topsecret"
        self.token = "secret-token"

        with responses.RequestsMock() as resps:
            resps.add(responses.POST, k.API_ENDPOINT + "/login",
                    json={"token": self.token})

            self.k = k.Kbg(self.email, self.password)

            self.assertEqual(1, len(resps.calls))

    @responses.activate
    def test_internals_token(self):
        self.assertEqual(self.token, self.k._token)

    @responses.activate
    def test_logged_in(self):
        self.assertTrue(self.k.logged_in())

    def test_get_consumer_information(self):
        consumer = {
            "email": self.email,
            "some": "field",
            "another": "one",
            "yes": True,
            "no": False,
        }

        with responses.RequestsMock() as resps:
            resps.add(responses.GET, k.API_ENDPOINT + "/api/consumer",
                    json={"consumer": consumer})

            got_consumer = self.k.get_consumer_information()

            self.assertEqual(1, len(resps.calls))
            headers = resps.calls[0].request.headers
            self.assertIn("Authorization", headers)
            self.assertEqual("Bearer %s" % self.token,
                    headers["Authorization"])

        self.assertEqual(consumer, got_consumer)
