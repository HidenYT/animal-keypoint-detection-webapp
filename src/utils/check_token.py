from functools import wraps

from django.conf import settings
from django.http import HttpRequest, HttpResponse


def check_token(view):
    @wraps(view)
    def wrapper(request: HttpRequest, *args, **kwargs):
        auth = request.headers.get("Authorization")
        if auth is None or auth != settings.MICROSERVICES_AUTH_TOKEN:
            return HttpResponse('Unauthorized', status=401)
        return view(request, *args, **kwargs)
    return wrapper
