import itertools
import uuid
import re
import typing as t
from django.conf import settings
from django.contrib.postgres import fields
from django.db import models, transaction
from os import path

from core.utils import file_drivers, language_parsers


def text_authors_default():
    return {"authors": [{"name": ""}]}


class Text(models.Model):
    """
    Main object ro store information about individual text
    """
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    root_section = models.OneToOneField('Section', related_name='+', null=True, default=None,
                                        on_delete=models.SET_NULL, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)

    name = models.TextField(blank=False, null=False)
    file_path = models.FileField(upload_to='uploads/text/')
    file_type = models.CharField(default='txt', max_length=8)

    authors = fields.JSONField(default=text_authors_default)
    language = models.CharField(default='ru', max_length=8)
    description = models.TextField(default='', blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.created.strftime("%H:%M:%S %d/%m/%Y")} - {self.name}'

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.pk or not self.root_section:
            self.root_section = Section.objects.create(text=self)
        super(Text, self).save(*args, **kwargs)

    @transaction.atomic
    def update_paragraph_entries(self):
        driver_class = settings.FILE_DRIVERS.get(self.file_type, None)
        parser_class = settings.LANGUAGE_PARSERS.get(self.language, None)
        if not driver_class:
            return  # todo error msg should be
        elif not parser_class:
            return
        else:
            driver: file_drivers.AbstractFileDriver = driver_class()
            parser: language_parsers.AbstractLanguageParser = parser_class()

        Paragraph.objects.filter(section__text=self).delete()
        with open(path.join(settings.MEDIA_ROOT, self.file_path.path), 'r') as tf:
            par_seq = driver.paragraph_sequence(tf)
            paragraphs_sentences = parser.parse(par_seq)
            Paragraph.save_sequence(paragraphs_sentences, self.root_section)

    def collect_sections(self):
        return Section.of_text(self.uid)


class Section(models.Model):
    """
    Store arbitrary tree structure.
    Important that structure given by Section's is only partition of Paragraph set.
    """
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.ForeignKey(Text, on_delete=models.CASCADE)

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None)
    following_sibling = models.ForeignKey('self', related_name='+', on_delete=models.SET_NULL,
                                          null=True, default=None)
    preceding_sibling = models.ForeignKey('self', related_name='+', on_delete=models.SET_NULL,
                                          null=True, default=None)
    from_paragraph = models.OneToOneField('Paragraph', related_name='+', on_delete=models.SET_NULL,
                                          null=True, default=None)
    to_paragraph = models.OneToOneField('Paragraph', related_name='+', on_delete=models.SET_NULL,
                                        null=True, default=None)

    subtitle = models.TextField(blank=True, null=False, default='')

    @staticmethod
    def build_json(sequence: t.Iterable['Section']):
        return list(map(lambda section: {
            'id': section.id,
            'parent': section.parent,
        }, sequence))

    @staticmethod
    def of_text(text_uid):
        return Section.objects.filter(text__uid=text_uid)

    @staticmethod
    def of_section(section_uid):
        return Section.objects.filter(parent__uid=section_uid)

    def sub(self) -> t.List['Section']:
        return Section.of_section(self.uid)

    def add_sub(self):
        Section.objects.create(parent=self, text=self.text)

    def sub_tree(self, flat=False, include_root=False):
        if flat:
            # inner include_root force appending sub sections and indent remains
            without_root = list(itertools.chain.from_iterable(
                s.sub_tree(flat=True, include_root=True)
                for s in self.sub()
            ))
            if not include_root:
                return without_root
            else:
                return [(self, 0)] \
                       + [(s, i + 1) for s, i in without_root]
        else:
            without_root = [(s, s.sub_tree(flat=False, include_root=False)) for s in self.sub()]
            if not include_root:
                return without_root
            else:
                return [(self, without_root)]

    def collect_paragraphs(self) -> t.List['Paragraph']:
        return Paragraph.objects.filter(section=self).order_by('serial_number')


class Paragraph(models.Model):
    """
    Smallest part of text as a bag of ideas.
    """
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    prev = models.OneToOneField('self', related_name='+',
                                on_delete=models.SET_NULL, null=True, default=None)
    next = models.OneToOneField('self', related_name='+',
                                on_delete=models.SET_NULL, null=True, default=None)

    serial_number = models.FloatField(null=True, default=None)
    raw_sentences = models.TextField(blank=True, null=False, default='')
    sentence_ids = fields.ArrayField(models.BigIntegerField(), null=True)
    language = models.CharField(max_length=8)     # per paragraph language

    def __str__(self):
        return self.raw_sentences[:64] + '..'

    def _create_sentence_objs(self, raw_sentences):
        self.sentence_ids = [
            Sentence.objects.create(paragraph=self, raw=s).id
            for s in raw_sentences
        ]
        self.save()

    def _set_previous(self, p: 'Paragraph'):
        self.prev = p
        self.save()

    def _set_next(self, p: 'Paragraph'):
        self.next = p
        self.save()

    @transaction.atomic
    def _set_sentences(self, sentence_ids):
        sentence_obj = Sentence.get_many(sentence_ids)
        self.sentence_ids = list(sentence_obj.values_list('id', flat=True))
        sentence_obj.update(paragraph=self)

        self.raw_sentences = ' '.join([s.raw for s in sentence_obj])
        self.save()

    @staticmethod
    def save_sequence(seq: t.Iterable[t.List[str]], section: Section, after: 'Paragraph' = None):
        prev = after
        for sentences in seq:
            serial = prev.serial_number + 1 if prev else 0
            created = Paragraph.objects.create(section=section, prev=prev,
                                               serial_number=serial, raw_sentences=' '.join(sentences))
            created._create_sentence_objs(sentences)
            # we touch each Paragraph two times: on create and to set next
            # it's more elegant to generate uid for next while before save current
            # also paragraph uid needs to create sentences, and sentence_ids could be set while creating Paragraph
            # if todo allocate next paragraph uid on previous sequence step
            if prev:
                prev._set_next(created)
            prev = created

    def save(self, *args, **kwargs):
        self.language = self.section.text.language
        super(Paragraph, self).save(*args, **kwargs)

    def sentences(self, raw=False):
        pk_list = self.sentence_ids
        sentence_objs = Sentence.get_many(pk_list)
        return [s.raw for s in sentence_objs] if raw else sentence_objs

    @transaction.atomic
    def concat(self, with_prev=True):   # will not update serial_numbers for now
        # N.B. assume now that current, prev and next all belong same section
        updated_sentence_ids = self.prev.sentence_ids + self.sentence_ids \
            if with_prev else self.sentence_ids + self.next.sentence_ids
        self._set_sentences(updated_sentence_ids)

        if with_prev:
            to_delete: Paragraph = self.prev
            after_that: Paragraph = to_delete.prev
            self.prev = to_delete.prev
            after_that.next = self
        else:
            to_delete: Paragraph = self.next
            after_that: Paragraph = to_delete.next
            self.next = to_delete.next
            after_that.prev = self

        deleting_uid = to_delete.uid
        to_delete.delete()
        self.save()
        after_that.save()

        return self.uid, deleting_uid, after_that.uid

    @transaction.atomic
    def split(self, after_sentence_id):
        actual_next = self.next
        new_paragraph = Paragraph(section=self.section, prev=self, next=self.next,
                                  serial_number=(self.serial_number + self.next.serial_number) / 2.,
                                  sentence_ids=None, language=self.language)
        self._set_next(new_paragraph)
        actual_next._set_previous(new_paragraph)

        actual_sentences = self.sentence_ids
        pos_split = actual_sentences.index(int(after_sentence_id)) + 1
        preserve, move = actual_sentences[:pos_split], actual_sentences[pos_split:]
        self._set_sentences(preserve)
        new_paragraph._set_sentences(move)

        return self, new_paragraph


class SectionEvent(models.Model):
    from core.utils import event_validators
    BUILD_SECTION = 'BUILD_SECTION'
    UNION_SECTION = 'UNION_SECTION'
    BORDER_SECTION = 'BORDER_SECTION'
    OFFSET_SECTION = 'OFFSET_SECTION'
    JOIN_SECTION = 'JOIN_SECTION'
    VALIDATORS: t.Dict[str, event_validators.EventValidator] = {
        BUILD_SECTION: event_validators.build_section,
        UNION_SECTION: event_validators.union_section,
        BORDER_SECTION: event_validators.border_section,
        OFFSET_SECTION: event_validators.offset_section,
        JOIN_SECTION: event_validators.join_section,
    }
    HANDLERS: t.Dict[str, t.Any] = {}

    id = models.BigIntegerField(primary_key=True)
    text = models.ForeignKey(Text, on_delete=models.CASCADE, null=False)
    session = models.ForeignKey(settings.SESSION_MODEL, on_delete=models.CASCADE, editable=False)
    EVENT_TYPES = (
        (BUILD_SECTION, 'build_section'),
        (UNION_SECTION, 'union_section'),
        (BORDER_SECTION, 'border_section'),
        (OFFSET_SECTION, 'offset_section'),
        (JOIN_SECTION, 'join_section'),
    )
    type = models.CharField(max_length=16, blank=False, choices=EVENT_TYPES)
    body = fields.JSONField(null=False, default=dict)
    canceled = models.BooleanField(null=False, default=False)

    @staticmethod
    def validate_event(event_type: str, event_body: dict) -> bool:
        validator = SectionEvent.VALIDATORS.get(event_type, None)
        return validator(event_type, event_body) if validator else False


class Sentence(models.Model):
    id = models.BigAutoField(primary_key=True)
    paragraph = models.ForeignKey(Paragraph, on_delete=models.CASCADE)

    raw = models.TextField()
    parts = fields.ArrayField(models.TextField())

    @staticmethod
    def clear_non_print(raw: str) -> str:
        return re.sub(r'  *', ' ', raw.replace('\n', ''))

    @staticmethod
    def get_many(ids):
        preserved = models.Case(*[models.When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
        return Sentence.objects.filter(id__in=ids).order_by(preserved)

    def save(self, *args, **kwargs):
        parser_class = settings.LANGUAGE_PARSERS.get(self.paragraph.language, None)
        if parser_class:
            parser = parser_class()
            _raw = Sentence.clear_non_print(self.raw)
            self.parts = list(filter(len, parser.parse_sentence(_raw)))
        super(Sentence, self).save(*args, **kwargs)

    def asObj(self: 'Sentence'):
        return {
            'id': self.id,
            'raw': self.raw
        }
