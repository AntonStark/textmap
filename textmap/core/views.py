import logging
from django.shortcuts import redirect, render, Http404
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from core.forms import TextForm
from core.models import Text, Section

log = logging.getLogger(__name__)


@login_required
@require_POST
def register_action(request):
    user, session = request.user, request.session
    log.debug(f'start with user={user}, session={session}')
    try:
        event_type = request.POST['type']
        event_body = request.POST['body']
        if not isinstance(event_body, dict):
            raise TypeError('event_body must be a dict')
    except KeyError:
        log.debug('request.POST missing fields')
        return HttpResponseBadRequest('missing fields \"type\" and/or \"body\"')
    except TypeError:
        log.debug('request.POST[\"body\"] not a dict')
        return HttpResponseBadRequest('event_body must be a dict')

    # todo authorisation and validation, then save and response with delta


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
def load_text(request):
    user = request.user
    if request.method == 'POST':
        form = TextForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponseBadRequest()

        text = form.save(commit=False)
        text.owner = user
        text.save()
        return redirect('text_info', text_id=text.pk)
    else:
        form = TextForm()

    return render(request, 'core/load_text.html', {'form': form})


def section_view(request, section_uid):
    try:
        section = Section.objects.get(uid=section_uid)
    except Section.DoesNotExist:
        raise Http404
    text = section.text
    sections_flat_tree = section.sub_tree(flat=True)
    par2sentences = {p.uid: p.sentences()
                     for p in section.collect_paragraphs()}

    context = {
        'text': text,
        'section': section,
        'sections_flat_tree': sections_flat_tree,
        'paragraphs': par2sentences
    }
    return render(request, 'core/section_view.html', context=context)
