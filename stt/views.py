import logging

from rest_framework import status, viewsets
from rest_framework.response import Response

from stt.models import Stt
from stt.utils import download_GAC, transcribe

logger = logging.getLogger(__name__)
download_GAC()


class SttViewSet(viewsets.ViewSet):

    def list(self, request):
        return Response(status=status.HTTP_200_OK, data=dict(ok=True))

    def create(self, request):
        fs = request.FILES['audio']

        audiorequest = Stt()
        audiorequest.audio.save(fs.name, fs)
        audiorequest.save()
        print(audiorequest.audio)

        resp = {}

        is_audio = False

        for ext in ['wav', 'flac']:
            if audiorequest.audio.name.endswith(ext):
                is_audio = True

        if not is_audio:
            return Response(status=status.HTTP_200_OK, data=dict(resp))

        res = transcribe(filename=audiorequest.audio.name)
        script = "\n".join(res)
        audiorequest.script = script
        audiorequest.save()
        resp['script'] = script

        return Response(status=status.HTTP_200_OK, data=dict(resp))
