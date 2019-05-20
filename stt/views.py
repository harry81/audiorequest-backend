import json
import logging

from constance import config
from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from main import __version__
from stt.models import Stt, task_process, Remember
from stt.utils import presigned_post, detect_web_uri

logger = logging.getLogger(__name__)


class SttViewSet(viewsets.ViewSet):

    def list(self, request):
        return Response(status=status.HTTP_200_OK, data=dict(ok=True))

    def retrieve(self, request, pk=None):
        try:
            stt = Stt.objects.get(uuid=pk)

        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=dict(ok=False, message=e.messages))

        except Stt.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data=dict(ok=False, message='No Stt'))

        res = stt.__dict__.copy()
        res.pop('_state')
        data = dict(ok=True, stt=res)

        return Response(status=status.HTTP_200_OK, data=data)

    def create(self, request):
        # step1) upload an audio file
        # step2) transcribe

        # step1
        key = request.POST.get('key')
        email = request.POST.get('email')
        language = request.POST.get('language', 'en-GB')
        channel = request.POST.get('channel', 1)

        if key:
            try:
                stt = Stt.objects.filter(audio=key).first()

                if not stt:
                    stt = Stt(audio=key)
                    stt.save()

            except Exception as e:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data=dict(ok=False, message=e.args[0]))

        else:
            sample_filename = 'stt_sample'
            stt = Stt.objects.filter(audio__contains=sample_filename).first()
            if not stt:
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data=dict(message="No sample containing containing [%s]" % sample_filename))

        # step2
        message = '성공적으로 요청이 되었습니다. '\
                  '곧(%d초 내) %s에서 내용확인이 가능합니다.' % (round(stt.duration, -1) + 10, email)
        res = dict(ok=True, message=message)

        try:
            task_process(pk=stt.id, email=email, language=language, channel=channel)
        except Exception as e:
            res = dict(ok=False, message=e.args[0])

        return Response(status=status.HTTP_200_OK, data=res)

    @action(methods=['get'], detail=False)
    def info(self, request, pk=None):
        data = dict(ok=True, version=__version__,
                    limit_anonymous=config.LIMIT_ANONYMOUS,
                    limit_user=config.LIMIT_USER)

        return Response(status=status.HTTP_200_OK, data=data)

    @action(methods=['patch'], detail=True)
    def notify(self, request, pk=None):
        email = request.POST.get('email')
        language = request.POST.get('language', 'en-GB')
        channel = request.POST.get('channel', 1)

        stt = Stt.objects.get(pk=pk)
        message = '성공적으로 요청이 되었습니다. '\
                  '곧(%d초 내) %s에서 내용확인이 가능합니다.' % (round(stt.duration, -1) + 10, email)
        res = dict(ok=True, message=message)

        try:
            task_process(pk=stt.id, email=email, language=language, channel=channel)
        except Exception as e:
            res = dict(ok=False, message=e.args[0])

        return Response(status=status.HTTP_200_OK, data=res)

    @action(methods=['get'], detail=False)
    def get_presigned_post(self, request):
        filename = request.GET.get('filename')
        try:
            response = presigned_post(filename)
        except Exception as e:
            response = e.args[0]
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data=response)

        return Response(status=status.HTTP_200_OK, data=response)


class KakaoViewSet(viewsets.GenericViewSet):
    puthentication_classes = ()

    def create(self, request):
        body = json.loads(request.body)
        utterance = body['userRequest']['utterance']

        if 'http' in utterance:
            return self.post_image(request)

        try:
            intent = body['intent']['name']
            func = getattr(self, intent)
            print(body)
            return func(request)
        except AttributeError:
            data = {
                "contents": [
                    {
                        "type": "text",
                        "text": "%s" % intent
                    }
                ]
            }
            return Response(status=status.HTTP_200_OK, data=data)

    def retrieve(self, request, pk=None):
        return Response(status=status.HTTP_200_OK, data=dict(ok=True))

    def list_post(self, request):
        body = json.loads(request.body)

        if 'date' in body['action']['detailParams']:
            value = json.loads(body['action']['detailParams']['date']['value'])
            title = value['date']

        elif 'period' in body['action']['detailParams']:
            value = json.loads(body['action']['detailParams']['period']['value'])
            title = "%s %s" % (value['from']['date'], value['to']['date'])

        else:
            title = "조회"

        listItems = [dict(type="title", title=title)]

        for remember in Remember.objects.filter(user=request.user).order_by('-created_at')[:3]:
            print(remember)
            item = dict(type="item", title='item', description="The Chainsmokers", imageUrl=remember.image_file.url)
            listItems.append(item)

        print(listItems)

        data = {
            "contents": [
                {
                    "type": "card.list",
                    "cards": [
                        {
                            "listItems": listItems,
                            "buttons": [
                                {
                                    "type": "block",
                                    "label": "좋",
                                    "message": "좋아요 %2b 1  ab%2bcd",
                                    "data": {
                                    }
                                },
                                {
                                    "type": "link",
                                    "label": "재생하기",
                                    "data":
                                    {
                                        "webUrl": "http://www.melon.com/artist/timeline.htm?artistId=729264",
                                        "moUrl": "http://www.melon.com/artist/timeline.htm?artistId=729264",
                                        "pcUrl": "http://www.melon.com/artist/timeline.htm?artistId=729264",
                                        "pcCustomScheme": "http://www.melon.com/artist/timeline.htm?artistId=729264",
                                        "macCustomScheme": "http://www.melon.com/artist/timeline.htm?artistId=729264",
                                        "iosUrl": "melonios://",
                                        "iosStoreUrl": "http://www.melon.com/artist/timeline.htm?artistId=729264",
                                        "androidUrl": "http://www.melon.com/artist/timeline.htm?artistId=729264",
                                        "androidStoreUrl": "http://www.melon.com/artist/timeline.htm?artistId=729264"
                                    }
                                }
                            ]
                        }
                    ]
                }
            ],
            "quickReplies": [
                {
                    "type": "text",
                    "label": "리스트카드 소스",
                    "message": "리스트카드 소스"
                },
                {
                    "type": "text",
                    "label": "데모",
                    "message": "데모"
                },
                {
                    "type": "text",
                    "label": "텍스트카드",
                    "message": "텍스트카드"
                },
                {
                    "type": "text",
                    "label": "커머스카드",
                    "message": "커머스카드"
                },
                {
                    "type": "text",
                    "label": "뮤직카드",
                    "message": "뮤직카드"
                },
                {
                    "type": "text",
                    "label": "리스트카드",
                    "message": "리스트카드"
                }
            ]
        }
        return Response(status=status.HTTP_200_OK, data=data)

    def post_image(self, request):
        entity = '통닭'
        body = json.loads(request.body)
        utterance = body['userRequest']['utterance']

        if 'http' in utterance:
            remember = Remember(image_url=utterance, user=request.user)
            remember.save()

            uri = "gs://%s/%s" % ('pointer-bucket', remember.image_file.name)
            annotations = detect_web_uri(uri)
            entity = ", ".join([ele.description for ele in annotations.web_entities[:5]])

        print(entity)
        data = {
            "contents": [
                {
                    "type": "text",
                    "text": "%s" % entity
                }
            ]
        }
        return Response(status=status.HTTP_200_OK, data=data)
