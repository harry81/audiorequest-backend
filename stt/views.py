import logging

from rest_framework import status, viewsets
from rest_framework.response import Response
from constance import config

from stt.models import Stt
from stt.utils import download_GAC

logger = logging.getLogger(__name__)
download_GAC()


class SttViewSet(viewsets.ViewSet):

    def list(self, request):
        return Response(status=status.HTTP_200_OK, data=dict(ok=True))

    def create(self, request):
        fs = request.FILES['audio']

        stt = Stt()
        stt.audio.save(fs.name, fs)
        stt.set_length()

        resp = {}

        is_audio = False

        for ext in ['wav', 'flac']:
            if stt.audio.name.endswith(ext):
                is_audio = True

        if stt.duration > config.LIMIT_ANONYMOUS:
            resp['script'] = '%d 초 이하의 wav 파일만 가능합니다요 : %d' % (config.LIMIT_ANONYMOUS, stt.duration)
            return Response(status=status.HTTP_200_OK, data=dict(resp))

        if not is_audio:
            return Response(status=status.HTTP_200_OK, data=dict(resp))

        stt.transcribe()
        stt.notify()
        resp['script'] = stt.script

        return Response(status=status.HTTP_200_OK, data=dict(resp))
