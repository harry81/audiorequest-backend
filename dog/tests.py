from rest_framework.test import APITransactionTestCase

from .tasks import daily_report


class DogTests(APITransactionTestCase):

    def test_daily_report(self):
        daily_report()
