import logging
from django.core.exceptions import ValidationError
from constance import config
from main import __version__
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from stt.models import Stt, task_process

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
        fs = request.FILES.get('audio')

        if fs:
            try:
                stt = Stt.objects.filter(audio__contains=fs.name).first()
                if not stt:
                    stt = Stt()
                    stt.audio.save(fs.name, fs)
                    stt.set_audio_meta()

            except Exception as e:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data=dict(ok=False, message=e.args[0]))
        else:
            sample_filename = 'stt_sample'
            stt = Stt.objects.filter(audio__contains=sample_filename).first()
            if not stt:
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data=dict(message="No sample containing containing [%s]" % sample_filename))

        return Response(status=status.HTTP_200_OK,
                        data=dict(id=stt.id, path=stt.hearable_audio_url, size=stt.audio.size))

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
