from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string


def list(request):
    content = render_to_string('vkgroup/list/index.html', {'title': 'VK groups list'})
    return HttpResponse(status=201, content=content)
