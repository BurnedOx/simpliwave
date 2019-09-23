import datetime
from django.conf import settings
from django.core.cache import cache
from .models import ClientProfile


class ActiveClientMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = datetime.datetime.now()
            current_user = request.user
            if len(current_user.groups.all()) == 1 and current_user.groups.all()[0].name == 'client':
                try:
                    ClientProfile.objects.get(user=current_user)
                except ClientProfile.DoesNotExist:
                    ClientProfile.objects.create(user=current_user)
                finally:
                    cache.set('last_seen_%s' % current_user.username, now,
                              settings.USER_LASTSEEN_TIMEOUT)
        response = self.get_response(request)
        return response
