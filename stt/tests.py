from rest_framework.test import APITransactionTestCase
import requests

from stt.utils import presigned_post


class SttTests(APITransactionTestCase):

    def test_basic(self):
        url = '/stt/info/'
        response = self.client.get(url, format='json')
        self.assertIn('limit_anonymous', response.json())

    def test_presigned_post(self):
        filename = 'temp.mp3'
        response_post = presigned_post(filename)
        self.assertIn('fields', response_post)
        files = {'file': b'test'}

        res = requests.post(response_post['url'], data=response_post['fields'], files=files)
        self.assertTrue(res.status_code, 204)

    # def test_send_email(self):
    #     send_email(to_addresses=['n_pointer@naver.com'],
    #                subject='subject from test', text='content', html='<b>hello</b>')
