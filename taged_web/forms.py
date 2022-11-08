from django import forms
from ckeditor.widgets import CKEditorWidget


class PostForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput({"placeholder": "Название заметки"}),
    )
    tags_checked = forms.CharField(max_length=255, required=True)
    input = forms.CharField(widget=CKEditorWidget(), required=True)
