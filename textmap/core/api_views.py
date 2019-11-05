from django.http import JsonResponse
from rest_framework.decorators import api_view

from core.views import log


@api_view(['GET'])
def get_paragraphs(request, text_id):
    log.debug(f'start, text_id={text_id}')
    return JsonResponse({'status': 'ok'}, status=200)
