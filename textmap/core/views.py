import logging
from rest_framework.decorators import api_view
from django.http.response import JsonResponse

log = logging.getLogger(__name__)


@api_view(['GET'])
def get_paragraphs(request, text_id):
    log.debug(f'start, text_id={text_id}')
    return JsonResponse({'status': 'ok'}, status=200)
