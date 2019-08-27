from django import forms

class UpdateForm(forms.Form):
    form_id = forms.IntegerField(widget=forms.HiddenInput())
    CHOICES=[(0, 'Not Financial'),
             (1, 'Negative'),
             (2, 'Indifferent'),
             (3, 'Positive')]
    choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)