import json
import logging

from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'kakao' not in request.path:
            return

        if not request.user.is_anonymous or (not request.body):
            return None

        body = json.loads(request.body)
        username = body['userRequest']['user']['id']

        defaults = dict(username=username)

        if not username:
            logger.info("No user id %s" % (body))

        user, _ = User.objects.get_or_create(username=username, defaults=defaults)
