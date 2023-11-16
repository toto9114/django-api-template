from django.shortcuts import render
from common_lib.response import CommonResponse
from rest_framework import status
# Create your views here.


def hello_world(request):
    return CommonResponse(status=status.HTTP_200_OK, data={'message': 'Hello World'})
