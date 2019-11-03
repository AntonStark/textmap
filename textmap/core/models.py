import uuid
from django.conf import settings
from django.contrib.postgres import fields
from django.db import models


class Text(models.Model):
    """
    Main object ro store information about individual text
    """
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    root_uid = models.OneToOneField('Part', related_name='+', null=True, default=None,
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


class Part(models.Model):
    """
    Store arbitrary tree structure
    """
    id = models.BigAutoField(primary_key=True)
    text = models.ForeignKey(Text, on_delete=models.CASCADE)
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE)

    subtitle = models.TextField(blank=True, null=False, default='')


class Paragraph(models.Model):
    """
    Smallest part of text as a bag of ideas.
    """
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    prev = models.OneToOneField('self', related_name='+',
                                on_delete=models.SET_NULL, null=True, default=None)
    next = models.OneToOneField('self', related_name='+',
                                on_delete=models.SET_NULL, null=True, default=None)
    sentence_ids = fields.ArrayField(models.BigIntegerField())


class Sentence(models.Model):
    id = models.BigAutoField(primary_key=True)
    paragraph = models.ForeignKey(Paragraph, on_delete=models.CASCADE)

    raw = models.TextField()
