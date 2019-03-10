from rest_framework.test import APITransactionTestCase
from joonggonara.tasks import fetch_joonggonara


class JoonggonaraTests(APITransactionTestCase):

    def test_basic(self):
        res = fetch_joonggonara()
        self.assertIn('category', res[0].keys())
