from django import forms

from .models import Post
from . import settings


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        exclude = ('author',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].help_text = None

    def clean_text(self):
        data = self.cleaned_data['text']
        if len(data) < settings.TEXT_LENGTH_MINIMAL:
            raise forms.ValidationError('Текст публикации не может быть короче'
                                        ' 10 символов.')
        return data
