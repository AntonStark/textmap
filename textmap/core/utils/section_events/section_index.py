import uuid
from functools import reduce

from core.models import Section


class SectionIndex:
    """Контейнер динамического состояния разделов текста"""
    def __init__(self, section_uid):
        target = Section.objects.get(uid=section_uid)
        sub_sections = target.sub()
        self._subs = {target: sub_sections}                                 # s -> sub[]
        self._parent = {target: target.parent}                              # s -> parent
        self._siblings = {s: [s.preceding_sibling, s.following_sibling]     # s -> [pre, fol]
                          for s in sub_sections}
        self._bounds = {target: [target.from_paragraph, target.to_paragraph]}   # s -> [from, to]
        self._par2sec = {p: target for p in target.collect_paragraphs()}        # p -> s

        sub_indices = [SectionIndex(sub) for sub in sub_sections]
        total = reduce(lambda d1, d2: d2 + d1, sub_indices, self)
        self._subs = total._subs
        self._parent = total._parent
        self._siblings = total._siblings
        self._bounds = total._bounds
        self._par2sec = total._par2sec

    def __add__(self, other: 'SectionIndex'):
        self._subs = {**other._subs, **self._subs}
        self._parent = {**other._parent, **self._parent}
        self._siblings = {**other._siblings, **self._siblings}
        self._bounds = {**other._bounds, **self._bounds}
        self._par2sec = {**other._par2sec, **self._par2sec}

    #
    #   Read methods
    def section(self, paragraph):
        return self._par2sec.get(paragraph, None)

    def same_section(self, p1, p2) -> bool:
        s1 = self.section(p1)
        s2 = self.section(p2)
        return s1 and s2 and s1 == s2

    def is_preceding_sibling(self, section, possible_sibling):
        return section and possible_sibling and section in self._siblings \
               and self._siblings[section][0] == possible_sibling

    def bounds(self, section):
        return self._bounds.get(section, None)

    def paragraph_diff(self, other: 'SectionIndex'):
        pass    # todo

    #
    #   Transformation methods
    def insert_proxy_section(self, actual_section):
        """
        actual_section была секцией нижнего уровня, а становится
        родителем новой секции нижнего уровня; все параграфы пееезжают туда
        """
        created_section = uuid.uuid4()
        self._subs[actual_section] = [created_section]
        self._parent[created_section] = actual_section
        self._siblings[created_section] = [None, None]
        self._bounds[actual_section] = [None, None]

        for p, s in self._par2sec.items():
            if s == actual_section:
                self._par2sec[p] = created_section
        return created_section

    def insert_preceding(self, target_section):
        parent = self._parent[target_section]

        new_section_uid = uuid.uuid4()
        self._subs[parent].append(new_section_uid)
        self._parent[new_section_uid] = parent

        prev_preceding = self._siblings[target_section][0]
        self._siblings[new_section_uid] = [prev_preceding, target_section]
        self._siblings[target_section][0] = new_section_uid

    def insert_following(self, target_section):
        parent = self._parent[target_section]

        new_section_uid = uuid.uuid4()
        self._subs[parent].append(new_section_uid)
        self._parent[new_section_uid] = parent

        prev_following = self._siblings[target_section][1]
        self._siblings[target_section][1] = new_section_uid
        self._siblings[new_section_uid] = [target_section, prev_following]

    def move_to_preceding(self, new_from_paragraph):
        """
        находим секцию C к которой относится new_from_paragraph и её from_paragraph
        у неё должна быть предшествующая
        согласованно меняем to_paragraph предшествующей и from_paragraph C
        """
        target_section = self._par2sec[new_from_paragraph]
        target_from = self._bounds[target_section][0]
        preceding_section = self._siblings[target_section][0]

        if not self._bounds[preceding_section][0]:  # preceding пустая
            self._bounds[preceding_section][0] = target_from
        self._bounds[preceding_section][1] = self._bounds[target_section][0] = new_from_paragraph
        # fixme для интервального [target_from, new_from_paragraph] изменения
        #  принадлежности в par2sec нужно отношение следования на параграфах

    def move_to_following(self, new_to_paragraph):
        """
        находим секцию C к которой относится new_to_paragraph и её to_paragraph
        у неё должна быть следуующая
        согласованно меняем from_paragraph следующей и to_paragraph C
        """
        new_section_uid = uuid.uuid4()
        # todo
