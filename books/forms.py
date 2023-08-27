from django import forms

from books.models import Comment


# Форма, для создания новой книги
class BookCreateFrom(forms.Form):
    title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput({"placeholder": "Название"}),
    )
    author = forms.CharField(
        max_length=100,
        widget=forms.TextInput({"placeholder": "Автор"}),
        required=True,
    )
    year = forms.DecimalField(
        max_digits=4,
        localize=True,
        required=False,
        widget=forms.TextInput({"placeholder": "Год"}),
    )
    about = forms.CharField(widget=forms.Textarea, label="Описание")


class SearchForm(forms.Form):
    search_text = forms.CharField(max_length=100, required=False)
    search_year = forms.DecimalField(
        max_digits=4, localize=True, widget=forms.TextInput, required=False
    )
    page = forms.IntegerField(min_value=1, required=False)


class CommentForm(forms.ModelForm):
    text = forms.CharField(min_length=10)

    class Meta:
        model = Comment
        fields = ["text", "rating"]
