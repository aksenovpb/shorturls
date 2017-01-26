from django.contrib.auth.forms import UserCreationForm
from authentication.models import Account


class SignupForm(UserCreationForm):

    class Meta:
        model = Account
        fields = ('email', 'username')
