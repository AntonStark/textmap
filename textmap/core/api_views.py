from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework.decorators import api_view

from core.models import Part
from core.views import log


@api_view(['GET'])
def get_parts(request, text_id):
    log.debug(f'start, text_id={text_id}')

    text_parts = Part.objects.filter(text__uid=text_id)
    # todo Part serializer
    return JsonResponse({'text_uid': text_id, 'parts': text_parts}, status=200)


@api_view(['GET'])
def parse_text(request, text_id):
    log.debug(f'start, text_id={text_id}')
    # todo utils
    return HttpResponseRedirect(redirect_to=reverse('text_info', args=[text_id]))
