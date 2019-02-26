import logging

from constance import config
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from stt.models import Stt, task_process


logger = logging.getLogger(__name__)


class SttViewSet(viewsets.ViewSet):

    def list(self, request):
        return Response(status=status.HTTP_200_OK, data=dict(ok=True))

    def create(self, request):
        fs = request.FILES['audio']

        try:
            stt = Stt()
            stt.audio.save(fs.name, fs)
            stt.set_audio_meta()
        except Exception as e:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data=dict(ok=False, message=e.args[0]))

        return Response(status=status.HTTP_200_OK, data=dict(id=stt.id, path=stt.audio.url, size=stt.audio.size))

    @action(methods=['patch'], detail=True)
    def transcribe(self, request, pk=None):
        is_audio = False
        resp = {}

        stt = Stt.objects.get(pk=pk)
        for ext in ['wav', 'flac']:
            if stt.audio.name.endswith(ext):
                is_audio = True

        if stt.duration > config.LIMIT_ANONYMOUS:
            resp['script'] = '%d 초 이하의 wav 파일만 가능합니다요 : %d' % (config.LIMIT_ANONYMOUS, stt.duration)
            return Response(status=status.HTTP_200_OK, data=dict(resp))

        if not is_audio:
            return Response(status=status.HTTP_200_OK, data=dict(resp))

        stt.transcribe()
        resp['script'] = stt.script

        return Response(status=status.HTTP_200_OK, data=dict(resp))

    @action(methods=['patch'], detail=True)
    def notify(self, request, pk=None):
        email = request.POST.get('email')
        language = request.POST.get('language', 'en-GB')
        channel = request.POST.get('channel', 1)

        stt = Stt.objects.get(pk=pk)
        res = dict(ok=True, message='%d초 내에 %s로 전송이 됩니다.' % (stt.duration, email))

        try:
            task_process(pk=stt.id, email=email, language=language, channel=channel)
        except Exception as e:
            res = dict(ok=False, message=e.args[0])

        return Response(status=status.HTTP_200_OK, data=res)
