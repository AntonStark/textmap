import logging
from django.shortcuts import render, Http404
from django.contrib.auth.decorators import login_required

from core.models import Text, Part, Paragraph

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
    parts = Part.objects.filter(text__uid=text.uid)

    context = {'text': text, 'parts': parts}
    return render(request, 'core/text_info.html', context=context)


def part_view(request, part_id):
    try:
        part = Part.objects.get(id=part_id)
    except Part.DoesNotExist:
        raise Http404
    text = part.text
    paragraph_list = Paragraph.objects.filter(part__id=part_id).order_by('serial_number')

    context = {'text': text, 'paragraph_list': paragraph_list}
    return render(request, 'core/part_view.html', context=context)
