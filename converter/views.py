from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello. Its converter")