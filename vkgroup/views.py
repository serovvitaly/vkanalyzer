from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect


def list(request):
    content = render_to_string('vkgroup/list/index.html', {'title': 'VK groups list'})
    return HttpResponse(content=content)


@csrf_protect
def find(request):
    import json
    post_data = json.loads(request.body.decode('utf8'))
    return JsonResponse(post_data)
