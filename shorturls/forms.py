from django import forms

from shorturls.models import Url
from shorturls.validators import validate_url


class UrlForm(forms.Form):
    url = forms.CharField()

    def clean_url(self):
        return validate_url(self.cleaned_data.get('url'))


class UrlFullForm(forms.ModelForm, UrlForm):

    class Meta:
        model = Url
        fields = 'url', 'description'

    def __init__(self, *args, **kwargs):
        super(UrlFullForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = False


class UrlChangeForm(forms.ModelForm):

    class Meta:
        model = Url
        fields = 'description', 'active'

    def __init__(self, *args, **kwargs):
        super(UrlChangeForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = False
