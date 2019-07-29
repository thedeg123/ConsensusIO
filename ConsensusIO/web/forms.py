from dal import autocomplete

from .models import Article
from django import forms


class PersonForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ('')