import uuid
import typing as t
from django.conf import settings
from django.contrib.postgres import fields
from django.db import models, transaction
from os import path

from core.utils import text_processing


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

    authors = fields.JSONField(default=dict)
    language = models.CharField(default='ru', max_length=8)
    description = models.TextField(default='', blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.created.strftime("%H:%M:%S %d/%m/%Y")} - {self.name}'

    def save(self, *args, **kwargs):
        if not self.pk or not self.root_section:
            self.root_section = Section.objects.create(text=self)
        super(Text, self).save(*args, **kwargs)

    @transaction.atomic
    def update_paragraph_entries(self):
        Paragraph.objects.filter(section__text=self).delete()

        par_seq = text_processing.paragraph_seq(path.join(settings.MEDIA_ROOT, self.file_path.path))
        Paragraph.save_sequence(par_seq, self.root_section)

    def collect_sections(self):
        return Section.objects.filter(text=self)


class Section(models.Model):
    """
    Store arbitrary tree structure.
    Important that structure given by Section's is only partition of Paragraph set.
    """
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.ForeignKey(Text, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               null=True, default=None)

    subtitle = models.TextField(blank=True, null=False, default='')

    @staticmethod
    def build_json(sequence: t.Iterable['Section']):
        return list(map(lambda part: {
            'id': part.id,
            'parent': part.parent,
        }, sequence))

    @staticmethod
    def of_text(text_uid):
        return Section.objects.filter(text__uid=text_uid)

    @staticmethod
    def of_section(section_uid):
        return Section.objects.filter(parent__uid=section_uid)

    @staticmethod
    def tree_view(section_list):
        pass

    def sub(self):
        return Section.of_section(self.uid)

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

    serial_number = models.IntegerField(null=True, default=None)
    raw_sentences = models.TextField(blank=True, null=False, default='')
    sentence_ids = fields.ArrayField(models.BigIntegerField(), null=True)

    def set_next(self, p: 'Paragraph'):
        self.next = p
        self.save()

    @staticmethod
    def save_sequence(seq, section: Section, after: 'Paragraph' = None):
        prev = after
        for s in seq:
            serial = prev.serial_number + 1 if prev else 0
            created = Paragraph.objects.create(section=section, prev=prev,
                                               serial_number=serial, raw_sentences=s)
            # we touch each Paragraph two times: on create and to set next
            # it's more elegant to generate uid for next while before save current
            if prev:
                prev.set_next(created)
            prev = created


class Sentence(models.Model):
    id = models.BigAutoField(primary_key=True)
    paragraph = models.ForeignKey(Paragraph, on_delete=models.CASCADE)

    raw = models.TextField()
