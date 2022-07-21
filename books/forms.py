from django import forms


class BookCreateFrom(forms.Form):
    title = forms.CharField(
        max_length=100,
        required=True,
        label='',
        widget=forms.TextInput({'placeholder': 'Название'})
    )
    author = forms.CharField(
        max_length=100, label='', widget=forms.TextInput({'placeholder': 'Автор'}), required=False
    )
    year = forms.DecimalField(
        max_digits=4, localize=True, label='', required=False,
        widget=forms.TextInput({'placeholder': 'Год'})
    )
    about = forms.CharField(widget=forms.Textarea, label='Описание')


class SearchForm(forms.Form):
    search_text = forms.CharField(
        max_length=100, required=False
    )
    search_year = forms.DecimalField(
        max_digits=4, localize=True, widget=forms.TextInput, required=False
    )
