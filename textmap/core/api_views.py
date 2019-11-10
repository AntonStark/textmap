from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework.decorators import api_view

from core.models import Part, Text
from core.views import log


# STAFF

@api_view(['GET'])
def parse_text(_, text_id):
    log.debug(f'start, text_uid={text_id}')
    try:
        text = Text.objects.get(uid=text_id)
    except Text.DoesNotExist:
        log.debug(f'not found, request for text_uid={text_id}')
        return JsonResponse({'error': 'text not found', 'text_id': text_id}, status=404)
    else:
        text.update_paragraph_entries()
        log.debug(f'successfully updated text_uid={text_id}')
    return HttpResponseRedirect(redirect_to=reverse('text_info', args=[text_id]))


# PART

@api_view(['GET'])
def text_parts(_, text_uid):
    """
    Observe all parts of text

    :param text_uid: uid of text to observe
    :return: JsonResponse in form {text_uid, parts: [{id, parent}, ]}
    """
    log.debug(f'start, text_uid={text_uid}')
    parts = Part.build_json(Part.objects.filter(text__uid=text_uid))
    log.debug(f'done, text_uid={text_uid}')
    return JsonResponse({'text_uid': text_uid, 'parts': parts}, status=200)


@api_view(['GET'])
def sub_parts(_, part_id):
    """
    Observe sub-parts of given part

    :param part_id: id of part to observe
    :return: JsonResponse in form {text_uid, parts: [{id, parent}, ]}
    """
    log.debug(f'start, part_id={part_id}')
    parts = Part.build_json(Part.objects.filter(parent__id=part_id))
    log.debug(f'done, part_id={part_id}')
    return JsonResponse({'part_id': part_id, 'parts': parts}, status=200)
