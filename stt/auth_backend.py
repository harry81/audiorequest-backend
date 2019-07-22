import json
import logging

from django.contrib.auth import get_user_model
from rest_framework import authentication

User = get_user_model()
logger = logging.getLogger(__name__)


class KakaoAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        body = json.loads(request.body)
        try:
            username = body['userRequest']['user']['id']
        except KeyError as e:
            print(e)
            return (None, None)

        defaults = dict(username=username)

        if not username:
            logger.info("No user id %s" % (body))

        user, _ = User.objects.get_or_create(username=username, defaults=defaults)

        return (user, None)
