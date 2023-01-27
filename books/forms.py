from django import forms


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
