from ckeditor.widgets import CKEditorWidget
from django import forms

from .models import Tags


class TagsField(forms.CharField):
    def to_python(self, value: str):
        """
        value == 'python, mysql, django'

        :return: ['python', 'mysql', 'django']
        """
        print(value)
        return value


class PostForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Название заметки",
                "class": "bg-body text-body",
            }
        ),
    )
    tags_in = forms.ModelMultipleChoiceField(queryset=Tags.objects.all(), to_field_name="tag_name")
    input = forms.CharField(widget=CKEditorWidget(), required=True)
