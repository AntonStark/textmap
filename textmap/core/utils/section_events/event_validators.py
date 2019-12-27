import typing as t
from operator import itemgetter

from core.models import Paragraph
from core.utils.section_events.section_index import SectionIndex

EventValidator = t.Callable[[SectionIndex, dict], t.Dict[str, Paragraph]]


def unpack_check_existence(body: dict, fields: t.List[str]) -> t.Tuple:
    pattern = itemgetter(*fields)
    try:
        args = pattern(body)
    except KeyError:
        return ()
    try:
        unpack = [Paragraph.objects.get(uid=a) for a in args]
    except Paragraph.DoesNotExist:
        return ()
    return tuple(unpack)


def build_section(section_index: SectionIndex, event_body: dict) -> t.Dict[str, Paragraph]:
    keys = ['from_paragraph', 'to_paragraph']
    fp, tp = unpack_check_existence(event_body, keys)
    fp_section, tp_section = section_index.section(fp), section_index.section(tp)

    if fp_section and tp_section \
            and fp_section == tp_section:
        checked = [fp, tp]
    else:
        checked = []
    return dict(zip(keys, checked))


def union_section(section_index: SectionIndex, event_body: dict) -> t.Dict[str, Paragraph]:
    keys = ['from_paragraph']
    fp, = unpack_check_existence(event_body, keys)
    prev = fp.prev
    prev_section = section_index.section(prev)
    fp_section = section_index.section(fp)

    if prev_section and fp_section \
            and section_index.is_preceding_sibling(fp_section, prev_section):
        checked = [fp]
    else:
        checked = []
    return dict(zip(keys, checked))


def border_section(section_index: SectionIndex, event_body: dict) -> t.Dict[str, Paragraph]:
    keys = ['prev_from_paragraph', 'next_from_paragraph']
    prev_from, next_from = unpack_check_existence(event_body, keys)

    if not section_index.same_section(prev_from, next_from):
        return {}

    prev_section = section_index.section(prev_from.prev)
    pf_section = section_index.section(prev_from)
    if section_index.is_preceding_sibling(pf_section, prev_section):
        checked = [prev_from, next_from]
    else:
        checked = []
    return dict(zip(keys, checked))


def offset_section(section_index: SectionIndex, event_body: dict) -> t.Dict[str, Paragraph]:
    keys = ['prev_from_paragraph', 'next_from_paragraph']
    prev_from, next_from = unpack_check_existence(event_body, keys)

    if not section_index.same_section(prev_from, next_from):
        return {}

    prev_section = section_index.section(prev_from.prev)
    pf_section = section_index.section(prev_from)
    if prev_section != pf_section:
        checked = [prev_from, next_from]
    else:
        checked = []
    return dict(zip(keys, checked))


def join_section(section_index: SectionIndex, event_body: dict) -> t.Dict[str, Paragraph]:
    keys = ['paragraph']
    paragraph, = unpack_check_existence(event_body, keys)
    section = section_index.section(paragraph)
    if section:
        checked = [paragraph]
    else:
        checked = []
    return dict(zip(keys, checked))
