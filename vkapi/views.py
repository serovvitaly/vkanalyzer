from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . import models


@csrf_exempt
def call(request):
    import json
    post_data = json.loads(request.body.decode('utf8'))
    api_call = models.ApiCall()
    api_call.data = post_data
    api_call.save()
    return HttpResponse(content='7d966987')
