from rest_framework.test import APITransactionTestCase
from stt.utils import send_email


class SttTests(APITransactionTestCase):

    def test_basic(self):
        # url = '/stt/'
        # test_file = SimpleUploadedFile("test.wav", b"file_content", content_type="audio/wav")
        # response = self.client.post(url, dict(audio=test_file))
        self.assertTrue(True)

    def test_send_email(self):
        send_email(to_addresses=['n_pointer@naver.com'],
                   subject='subject from test', text='content', html='<b>hello</b>')
