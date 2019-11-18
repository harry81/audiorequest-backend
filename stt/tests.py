import requests
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from stt.models import Remember
from stt.utils import presigned_post

User = get_user_model()


class ShelfTests(APITransactionTestCase):

    def setUp(self):
        User.objects.create(username='hi')

    def test_book(self):
        url = '/api/shelf/'
        data = dict(isbn="8975601994 9788975601996")
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_bookprogress(self):
        url = '/api/shelf/1/bookprogress/'
        data = dict(shelf_id=1, page=20)
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


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

    def test_list_post(self):
        url = '/api/kakao/'
        data = {'action': {'clientExtra': None,
                           'detailParams': {'date': {'groupName': 'period',
                                                     'origin': '내일',
                                                     'value': '{"dateTag": "tomorrow", '
                                                     '"dateHeadword": null, "month": '
                                                     'null, "year": null, "date": '
                                                     '"2019-05-21", "day": null}'}},
                           'id': '5cdfbf425f38dd5d3dfb3a34',
                           'name': 'request to hoodpub',
                           'params': {'date': '{"dateTag": "tomorrow", "dateHeadword": null, '
                                      '"month": null, "year": null, "date": '
                                      '"2019-05-21", "day": null}'}},
                'bot': {'id': '5cdfbded384c5578c43cc447!', 'name': 'local-hoodpub'},
                'contexts': [],
                'intent': {'extra': {'reason': {'code': 1, 'message': 'OK'}},
                           'id': '5cdfc5b8384c5578c43cc46a',
                           'name': 'list_post'},
                'userRequest': {
                    'block': {'id': '5cdfc5b8384c5578c43cc46a',
                              'name': 'list_post'},
                    'lang': 'kr',
                    'params': {'ignoreMe': 'true', 'surface': 'Mini'},
                    'timezone': 'Asia/Seoul',
                    'user': {'id': 'c0e84fe0abf9fcb43cfe5b2fedd1696f573c826ce797800e0bf25aac0652bf175c',
                             'properties': {
                                 'botUserKey': 'c0e84fe0abf9fcb43cfe5b2fedd1696f573c826ce797800e0bf25aac0652bf175c'},
                             'type': 'botUserKey'},
                    'utterance': '내일 보여줘'}}

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

        cnt = User.objects.all().count()
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(cnt < User.objects.all().count())
