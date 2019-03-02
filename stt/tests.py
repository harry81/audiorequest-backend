from rest_framework.test import APITransactionTestCase
# from stt.utils import send_email


class SttTests(APITransactionTestCase):

    def test_basic(self):
        url = '/stt/info/'
        response = self.client.get(url, format='json')
        self.assertIn('limit_anonymous', response.json())

    # def test_send_email(self):
    #     send_email(to_addresses=['n_pointer@naver.com'],
    #                subject='subject from test', text='content', html='<b>hello</b>')
