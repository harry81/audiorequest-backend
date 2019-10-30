import json
import logging

from constance import config
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from main import __version__
from stt.models import Remember, Stt, task_process
from stt.utils import presigned_post, send_email
from water.krawler import Chosun, Hani

krawler_modules = dict(hani=Hani, chosun=Chosun)

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
    puthentication_classes = ('stt.auth_backend.KakaoAuthentication', )

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

        # 입력된 사진이 없다면 사용자에게 등록을 요구한다.
        if not Remember.objects.filter(user=request.user).order_by('-created_at'):
            data = {"contents": [
                dict(type='text', text="사진을 입력해 주세요")
            ]}
            return Response(status=status.HTTP_200_OK, data=data)

        if 'date' in body['action']['detailParams']:
            value = json.loads(body['action']['detailParams']['date']['value'])
            title = value['date']

        elif 'period' in body['action']['detailParams']:
            value = json.loads(body['action']['detailParams']['period']['value'])
            title = "%s %s" % (value['from']['date'], value['to']['date'])

        else:
            title = "보자"

        listItems = []

        for remember in Remember.objects.filter(user=request.user).order_by('-created_at')[:5]:
            tag_names = ", ".join([tag.name for tag in remember.tags.all()[:3]])
            when = timezone.localtime(remember.created_at).strftime('%y-%m-%d %I%P')
            item = dict(type="item", title="%s" % tag_names, description=when,
                        imageUrl=remember.image_file.thumbnail['250x250'].url,
                        link={"web": remember.image_file.url})
            listItems.append(item)

        data = {
            "version": "2.0",
            "template":
            {
                "outputs": [
                    {
                        "type": "listCard",
                        "cards": [
                            {
                                "listItems": listItems
                            }
                        ]
                    }
                ]}
        }

        data = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "listCard": {
                            "header": {
                                "title": title,
                                "imageUrl": "http://k.kakaocdn.net/dn/xsBdT/btqqIzbK4Hc/F39JI8XNVDMP9jPvoVdxl1/2x1.jpg"
                            },
                            "items": listItems
                        }
                    }
                ]
            }
        }
        return Response(status=status.HTTP_200_OK, data=data)

    def post_image(self, request):
        entity = 'hoodpub'
        body = json.loads(request.body)
        utterance = body['userRequest']['utterance']

        if 'http' in utterance:
            remember = Remember(image_url=utterance, user=request.user)
            remember.save()
            entity = remember.get_tags()

        data = {
            "contents": [
                {
                    "type": "text",
                    "text": "%s" % ", ".join([ele for ele in entity])
                }
            ]
        }
        return Response(status=status.HTTP_200_OK, data=data)

    def show_version(self, request):
        data = {
            "contents": [dict(type='text', text=__version__)]
        }
        return Response(status=status.HTTP_200_OK, data=data)


class DogViewSet(viewsets.ViewSet):

    def create(self, request):
        send_email(**request.data)

        return Response(status=status.HTTP_200_OK)


@permission_classes((AllowAny, ))
class PugViewSet(viewsets.ViewSet):

    def list(self, request):
        dest = request.query_params.get('dest', 'hani')
        cls = krawler_modules[dest]
        krawler = cls()

        articles = []
        for cnt in range(0, 5):
            articles.append(krawler.article(index=cnt))

        return Response(status=status.HTTP_200_OK, data=articles)
