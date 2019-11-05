import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

log = logging.getLogger(__name__)


@login_required()
def user_home(request):
    log.debug(f'start with user={request.user}')
    context = {'user': request.user}
    return render(request, 'core/user_home.html', context=context)


def get_text(request, text_id):
    context = {'text_id': text_id}
    return render(request, 'core/get_text.html', context=context)
