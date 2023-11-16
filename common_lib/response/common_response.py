import ujson as json
from django.http import HttpResponse


class CommonResponse(HttpResponse):
    def __init__(self, data, status=None, message=None):
        super().__init__(content_type='application/json', status=status)
        self.data = data
        self.message = message
        self.content = self.render_content()

    def render_content(self):
        if self.message is None and 200 <= self.status_code < 300:
            self.message = 'OK'
        response = {
            'meta': {'code': self.status_code, 'message': self.message},
            'data': self.data
        }
        return json.dumps(response)
