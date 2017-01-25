from django import forms

from shorturls.validators import validate_url


class UrlForm(forms.Form):
    url = forms.CharField()

    def clean_url(self):
        return validate_url(self.cleaned_data.get('url'))
