from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework.decorators import api_view

from core.models import Section, Text
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
def text_sections(_, text_uid):
    """
    Observe all section of text

    :param text_uid: uid of text to observe
    :return: JsonResponse in form {text_uid, sections: [{id, parent}, ]}
    """
    log.debug(f'start, text_uid={text_uid}')
    parts = Section.build_json(Section.of_text(text_uid))
    log.debug(f'done, text_uid={text_uid}')
    return JsonResponse({'text_uid': text_uid, 'sections': parts}, status=200)


@api_view(['GET'])
def sub_sections(_, section_uid):
    """
    Observe sub-sections of given part

    :param section_uid: id of part to observe
    :return: JsonResponse in form {section_id, sections: [{id, parent}, ]}
    """
    log.debug(f'start, part_id={section_uid}')
    parts = Section.build_json(Section.of_section(section_uid))
    log.debug(f'done, part_id={section_uid}')
    return JsonResponse({'section_id': section_uid, 'sections': parts}, status=200)
