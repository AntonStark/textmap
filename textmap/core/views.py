import json
import logging
from django.shortcuts import render, Http404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from core.models import Text, Section, SectionEvent
from core.utils.section_events.section_index import SectionIndex

log = logging.getLogger(__name__)


@login_required
def user_home(request):
    log.debug(f'start with user={request.user}')
    user = request.user
    context = {
        'user': request.user,
        'texts': Text.objects.filter(owner=user),
    }
    return render(request, 'core/user_home.html', context=context)


def text_info(request, text_id):
    try:
        text = Text.objects.get(uid=text_id)
    except Text.DoesNotExist:
        raise Http404
    root_section = text.root_section
    sections_flat_tree = root_section.sub_tree(flat=True, include_root=True)

    context = {'text': text, 'section': root_section, 'sections_flat_tree': sections_flat_tree}
    return render(request, 'core/text_info.html', context=context)


@login_required
@require_POST
def register_action(request, text_id):
    user, session = request.user, request.session
    log.debug(f'start with user={user}, session={session}')
    try:
        request.data = json.loads(request.body)
    except json.JSONDecodeError:
        log.debug(f'JSONDecodeError, request.body={request.body}')
        return JsonResponse({'error': 'request data not a valid json'}, status=400)
    except Exception as exc:
        log.debug(exc)

    try:
        event_type = request.data['type']
        event_body = request.data['body']
        if not isinstance(event_body, dict):
            raise TypeError('event_body must be a dict')
    except KeyError as exc:
        log.debug(f'request.POST missing fields, user={user}')
        return JsonResponse({'error': f'request must contain field {exc.args[0]}'}, status=400)
    except TypeError:
        log.debug(f'request.POST[\"body\"] not a dict, user={user}')
        return JsonResponse({'error': 'field body must be a dict'}, status=400)

    try:
        target_text = Text.objects.get(uid=text_id)
    except Text.DoesNotExist:
        log.debug(f'text not found, text_id = {text_id}, user={user}')
        return JsonResponse({'error': 'text not found'}, status=404)
    if user != target_text.owner:
        log.debug(f'not authorized, user={user} text={target_text}')
        return JsonResponse({'error': 'not authorized'}, status=403)

    section_index = SectionIndex(target_text.root_section.uid)
    target_paragraphs = SectionEvent.validate_event(section_index, event_type, event_body)
    if not target_paragraphs:
        log.debug(f'wrong event description, user={user}')
        return JsonResponse({'error': f'wrong event description'}, status=400)

    # todo нужно переводить разницу двух SectionIndex в форму изменения принадлежности параграфов
    # todo save and response with delta


def section_view(request, section_uid):
    try:
        section = Section.objects.get(uid=section_uid)
    except Section.DoesNotExist:
        raise Http404
    text = section.text
    sections_flat_tree = section.sub_tree(flat=True)
    paragraph_list = section.collect_paragraphs()

    context = {
        'text': text,
        'section': section,
        'sections_flat_tree': sections_flat_tree,
        'paragraph_list': paragraph_list
    }
    return render(request, 'core/section_view.html', context=context)
