from django import forms

from core.models import Text


class TextForm(forms.ModelForm):
    class Meta:
        model = Text
        fields = ['name', 'file_path', 'authors']
        widgets = {
            'name': forms.TextInput(),
        }
        labels = {
            'name': 'Название',
            'file_path': 'Файл',
            'authors': 'Авторы',
        }


# class AuthorsField(forms.MultiValueField):
#     def __init__(self, **kwargs):
#         pass
