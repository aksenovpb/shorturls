from django.test import TestCase
from authentication.forms import RegistrationForm as SignupForm, PasswordResetForm, PasswordChangeForm, SetPasswordForm
from authentication.forms import AuthenticationForm as LoginForm
from authentication.models import Account


class AuthenticationFormsTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'user',
            'email': 'user@user.loc',
            'password': 'userpassword'
        }
        self.user, created = Account.objects.get_or_create(**{
            'username': self.user_data.get('username'),
            'email': self.user_data.get('email')
        })
        self.user.set_password(self.user_data.get('password'))
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
        post = {'username': 'user@notexists.loc', 'password': 'userpassword'}
        form = LoginForm(data=post)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            '__all__': [u'Please enter a correct email and password. Note that both fields may be case-sensitive.']
        })
        self.assertEqual(form.get_user(), None)

    def test_authentication_forms__setpasswordform__valid(self):
        post = {
            'new_password1': 'newvalidpassword',
            'new_password2': 'newvalidpassword'
        }
        form = SetPasswordForm(user=self.user, data=post)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.check_password(post.get('new_password1')))

    def test_authentication_forms__setpasswordform__not_valid(self):
        post = {
            'new_password1': 'newvalidpassword1',
            'new_password2': 'newvalidpassword2'
        }
        form = SetPasswordForm(user=self.user, data=post)
        self.assertFalse(form.is_valid())

    def test_authentication_forms__passwordresetform__valid(self):
        post = {'email': self.user.email}
        form = PasswordResetForm(post)
        self.assertTrue(form.is_valid())

    def test_authentication_forms__passwordresetform__not_exists(self):
        post = {'email': 'valid@valid.loc'}
        form = PasswordResetForm(post)
        self.assertFalse(form.is_valid())

    def test_authentication_forms__passwordresetform__not_valid(self):
        post = {'email': 'not valid.loc'}
        form = PasswordResetForm(post)
        self.assertFalse(form.is_valid())

    def test_authentication_forms__passwordchangeform__valid(self):
        post = {
            'old_password': self.user_data.get('password'),
            'new_password1': 'newvalidpassword',
            'new_password2': 'newvalidpassword'
        }
        form = PasswordChangeForm(user=self.user, data=post)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.check_password(post.get('new_password1')))

    def test_authentication_forms__passwordchangeform__not_valid(self):
        post = {
            'old_password': 'notvalid',
            'new_password1': 'newvalidpassword',
            'new_password2': 'newvalidpassword'
        }
        form = PasswordChangeForm(user=self.user, data=post)
        self.assertFalse(form.is_valid())

        post = {
            'old_password': self.user_data.get('password'),
            'new_password1': 'newvalidpassword1',
            'new_password2': 'newvalidpassword2'
        }
        form = PasswordChangeForm(user=self.user, data=post)
        self.assertFalse(form.is_valid())
