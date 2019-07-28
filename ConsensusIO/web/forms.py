from dal import autocomplete

from django import forms


class PersonForm(forms.ModelForm):
    birth_country = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        widget=autocomplete.ModelSelect2(url='index')
    )

    class Meta:
        model = Person
        fields = ('__all__')