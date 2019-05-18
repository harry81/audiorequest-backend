import requests
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from stt.utils import presigned_post
from stt.models import Remember


class SttTests(APITransactionTestCase):

    def test_get_info(self):
        url = '/api/stt/info/'
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
        url = '/api/stt/get_presigned_post/'
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
        url = '/api/stt/'
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
        url = '/api/stt/'
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
        url = '/api/stt/'
        response = self.client.post(url, data)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertIn('mono', response.data['message'])


class KakaoTests(APITransactionTestCase):

    def test_save_image(self):
        uri = 'http://dn-m.talk.kakao.com/talkm/bl29h5I7Vso/58Ts9emhMRxr7mU0h9R2Fk/i_uf0s78xwnb04.png'
        rem = Remember(image_url=uri)
        rem.save()
        print(rem)
        self.assertTrue(True)

    def test_post_text(self):
        url = '/api/kakao/'
        data = {'action': {'clientExtra': None,
                           'detailParams': {},
                           'id': '5cde98c1e82127459ccb103e',
                           'name': 'upload images',
                           'params': {}},
                'bot': {'id': '5cde7e03e82127459ccb0fff', 'name': 'foodtext'},
                'contexts': [],
                'intent': {'extra': {'reason': {'code': 1, 'message': 'OK'}},
                           'id': '5cde7e03e82127459ccb1003',
                           'name': '폴백 블록'},
                'userRequest': {'block': {'id': '5cde7e03e82127459ccb1003', 'name': '폴백 블록'},
                                'lang': 'kr',
                                'params': {'surface': 'Kakaotalk.plusfriend'},
                                'timezone': 'Asia/Seoul',
                                'user': {'id': 'c0d01a32a8225dfc645e72a5abdd3d1f2c3c826ce797800e0bf25aac0652bf175c',
                                         'properties': {'plusfriendUserKey': 'Pt5qtfZJhnxp'},
                                         'type': 'botUserKey'},
                                'utterance': 'what are you doing/'}}

        response = self.client.post(url, data=data, format='json')

    def test_post_image(self):
        uri = 'http://dn-m.talk.kakao.com/talkm/bl29h5I7Vso/58Ts9emhMRxr7mU0h9R2Fk/i_uf0s78xwnb04.png'
        url = '/api/kakao/'
        data = {'action': {'clientExtra': None,
                           'detailParams': {},
                           'id': '5cde98c1e82127459ccb103e',
                           'name': 'upload images',
                           'params': {}},
                'bot': {'id': '5cde7e03e82127459ccb0fff', 'name': 'foodtext'},
                'contexts': [],
                'intent': {'extra': {'reason': {'code': 1, 'message': 'OK'}},
                           'id': '5cde7e03e82127459ccb1003',
                           'name': '폴백 블록'},
                'userRequest': {'block': {'id': '5cde7e03e82127459ccb1003', 'name': '폴백 블록'},
                                'lang': 'kr',
                                'params': {'surface': 'Kakaotalk.plusfriend'},
                                'timezone': 'Asia/Seoul',
                                'user': {'id': 'c0d01a32a8225dfc645e72a5abdd3d1f2c3c826ce797800e0bf25aac0652bf175c',
                                         'properties': {'plusfriendUserKey': 'Pt5qtfZJhnxp'},
                                         'type': 'botUserKey'},
                                'utterance': uri}}

        response = self.client.post(url, data=data, format='json')
