from django.test import TestCase
from authentication.forms import SignupForm
from authentication.forms import LoginForm
from authentication.models import Account


class AuthenticationFormsTestCase(TestCase):
    def setUp(self):
        self.user, created = Account.objects.get_or_create(**{
            'username': 'user',
            'email': 'user@user.loc'
        })
        self.user.set_password('userpassword')
        self.user.save()

    def test_authentication_forms__signupform__blank(self):
        form = SignupForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'username': ['This field is required.'],
            'email': ['This field is required.'],
            'password1': ['This field is required.'],
            'password2': ['This field is required.']
        })

    def test_authentication_forms__signupform__valid(self):
        post = {
                'username': 'hello',
                'email': 'hello@world.loc',
                'password1': 'helloworld',
                'password2': 'helloworld'
        }
        form = SignupForm(post)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, post.get('username'))
        self.assertEqual(user.email, post.get('email'))
        self.assertTrue(user.check_password(post.get('password1')))

    def test_authentication_forms__signupform__valid_duplicate(self):
        post = {
                'username': 'user',
                'email': 'user@user.loc',
                'password1': 'userpassword',
                'password2': 'userpassword'
        }
        form = SignupForm(post)
        self.assertFalse(form.is_valid())

    def test_authentication_forms__signupform__not_valid(self):
        post = {
                'username': 'user'*20,
                'email': 'notvalid',
                'password1': 'valid_if_django_validation',
                'password2': 'valid_if_django_validation'
        }
        form = SignupForm(post)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'username': ['Ensure this value has at most 40 characters (it has 80).'],
            'email': ['Enter a valid email address.']
        })

    def test_authentication_forms__loginform__blank(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'username': ['This field is required.'],
            'password': ['This field is required.']
        })

    def test_authentication_forms__loginform__valid(self):
        post = {'username': 'user@user.loc', 'password': 'userpassword'}
        form = LoginForm(data=post)
        self.assertTrue(form.is_valid())
        self.assertEqual(self.user, form.get_user())

    def test_authentication_forms__loginform__not_valid(self):
        post={'username': 'user@notexists.loc', 'password': 'userpassword'}
        form = LoginForm(data=post)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            '__all__': [u'Please enter a correct email and password. Note that both fields may be case-sensitive.']
        })
        self.assertEqual(form.get_user(), None)
