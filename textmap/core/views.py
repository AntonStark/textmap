import logging
from django.shortcuts import render, Http404
from django.contrib.auth.decorators import login_required

from core.models import Text, Section

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
    sections = text.collect_sections()

    context = {'text': text, 'sections': sections}
    return render(request, 'core/text_info.html', context=context)


def section_view(request, section_uid):
    try:
        section = Section.objects.get(uid=section_uid)
    except Section.DoesNotExist:
        raise Http404
    text = section.text
    paragraph_list = section.collect_paragraphs()

    context = {'text': text, 'paragraph_list': paragraph_list}
    return render(request, 'core/section_view.html', context=context)
