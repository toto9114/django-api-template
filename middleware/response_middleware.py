from rest_framework import status
from common_lib.response.common_response import CommonResponse

class CommonResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)

            if isinstance(response, CommonResponse):
                return response

            status_code = response.status_code
            data = response.data
            message = response.reason_phrase
            return CommonResponse(status=status_code,
                                  message=message,
                                  data=data)
        except Exception:
            data = None
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            message = f'Internal Server Error'
            return CommonResponse(status=status_code,
                                  message=message,
                                  data=data)
