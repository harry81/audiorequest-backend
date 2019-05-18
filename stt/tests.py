import requests
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from stt.utils import presigned_post


class SttTests(APITransactionTestCase):

    def test_get_info(self):
        url = '/stt/stt/info/'
        response = self.client.get(url, format='json')
        self.assertIn('limit_anonymous', response.json())

    def test_presigned_post(self):
        filename = 'temp.mp3'
        response_post = presigned_post(filename)
        self.assertIn('fields', response_post)
        files = {'file': b'test'}

        res = requests.post(response_post['url'], data=response_post['fields'], files=files)
        self.assertTrue(res.status_code, 204)

    def test_post_jpg(self):
        filename = 'audio-test.jpg'
        url = '/stt/stt/get_presigned_post/'
        response = self.client.get(url, dict(filename=filename))
        self.assertTrue(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_post_wav(self):
        filename = 'audio-test.wav'
        response_post = presigned_post(filename)
        self.assertIn('fields', response_post)
        fp = open('./samples/%s' % filename, 'rb')
        files = {'file': fp.read()}

        res = requests.post(response_post['url'], data=response_post['fields'], files=files)
        self.assertTrue(res.status_code, status.HTTP_204_NO_CONTENT)

        data = dict(key=response_post['fields']['key'], email='chharry@gmail.com')
        url = '/stt/stt/'
        response = self.client.post(url, data)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertIn('mono', response.data['message'])

    def test_post_flac(self):
        filename = 'audio-test.flac'
        response_post = presigned_post(filename)
        self.assertIn('fields', response_post)
        fp = open('./samples/%s' % filename, 'rb')
        files = {'file': fp.read()}

        res = requests.post(response_post['url'], data=response_post['fields'], files=files)
        self.assertTrue(res.status_code, status.HTTP_204_NO_CONTENT)

        data = dict(key=response_post['fields']['key'], email='chharry@gmail.com')
        url = '/stt/stt/'
        response = self.client.post(url, data)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertIn('성공적', response.data['message'])

    def test_post_mp3(self):
        filename = 'audio-test.mp3'
        response_post = presigned_post(filename)
        self.assertIn('fields', response_post)
        fp = open('./samples/%s' % filename, 'rb')
        files = {'file': fp.read()}

        res = requests.post(response_post['url'], data=response_post['fields'], files=files)
        self.assertTrue(res.status_code, status.HTTP_204_NO_CONTENT)

        data = dict(key=response_post['fields']['key'], email='chharry@gmail.com')
        url = '/stt/stt/'
        response = self.client.post(url, data)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertIn('mono', response.data['message'])
