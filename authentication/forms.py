from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from authentication.models import Account


class SignupForm(UserCreationForm):

    class Meta:
        model = Account
        fields = ('email', 'username')


class LoginForm(AuthenticationForm):
    pass
