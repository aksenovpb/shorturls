from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.text import capfirst
from authentication.models import Account


class RegistrationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': 'The two password fields didn\'t match.'
    }

    password1 = forms.CharField(label='Password',
        widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
        widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = 'email', 'username'

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch'
            )
        password_validation.validate_password(password2, None)
        return password2

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class AuthenticationForm(forms.Form):
    username = forms.CharField(max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': 'Please enter a correct %(username)s and password. '
                         'Note that both fields may be case-sensitive.',
        'inactive': 'This account is inactive'
    }

    def __init__(self, request=None, *args, ** kwargs):
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)
        
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive'
            )

    def get_user_id(self):
        return self.user_cache.id if self.user_cache else None

    def get_user(self):
        return self.user_cache


class PasswordResetForm(forms.Form):
    pass


class SetPasswordForm(forms.Form):
    pass


class PasswordChangeForm(forms.Form):
    pass
