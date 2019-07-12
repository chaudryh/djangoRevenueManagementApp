from django.http import HttpResponse
import time

def testView(request):
    time.sleep(120)

    return HttpResponse('you get here')