import logging
from django.shortcuts import render, Http404
from django.contrib.auth.decorators import login_required

from core.models import Text

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

    context = {'text': text}
    return render(request, 'core/text_info.html', context=context)
