import json
from typing import Any
from urllib import request
from django.http import HttpResponse


class JSONHttpErrorResponse(HttpResponse):
    def __init__(self, response: HttpResponse) -> None:
        content = json.dumps({
            "code": response.status_code,
            "name": response.__class__.__name__[len("HttpResponse"):],
            "description": response.content.decode(),
        })
        self.status_code = response.status_code
        super().__init__(content, content_type="application/json")
        