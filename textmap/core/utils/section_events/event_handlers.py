import copy
import typing as t

from core.models import Paragraph, Section
from core.utils.section_events.event_validators import unpack_check_existence
from core.utils.section_events import section_index as si

SectionIndexDiff = t.Dict[Paragraph, Section]


class AbstractHandler:
    @staticmethod
    def handle(sec_index: si.SectionIndex, event_body: t.Dict[str, Paragraph])\
            -> t.Tuple[si.SectionIndex, SectionIndexDiff]:
        pass


class BuildSection(AbstractHandler):
    @staticmethod
    def handle(index: si.SectionIndex, event_body: t.Dict[str, Paragraph]) \
            -> t.Tuple[si.SectionIndex, SectionIndexDiff]:
        keys = ['from_paragraph', 'to_paragraph']
        fp, tp = unpack_check_existence(event_body, keys)
        index_snapshot = copy.deepcopy(index)

        editing_section = index.section(fp)
        pf, pl = index._bounds[editing_section]

        need_before, need_after = fp != pf, tp != pl
        editing_section = index.insert_proxy_section(editing_section)
        if need_before:
            index.insert_preceding(editing_section)
            index.move_to_preceding(fp)
        if need_after:
            index.insert_following(editing_section)
            index.move_to_following(tp)

        par_diff = index.paragraph_diff(index_snapshot)
        return index, par_diff
