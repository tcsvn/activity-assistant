from django import forms

class ModelForm(forms.Form):
    modelfile = forms.FileField(
        label='Select a file that contains the model',
        help_text='max. 42 megabytes'
    )