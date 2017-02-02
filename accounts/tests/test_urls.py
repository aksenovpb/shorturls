from django.test import TestCase
from django.urls import reverse


class AccountsUrlsTestCase(TestCase):
    def test_accounts_urls__profile(self):
        self.assertEqual(reverse('accounts:profile'), '/accounts/profile/')

    def test_accounts_urls__change_password(self):
        self.assertEqual(reverse('accounts:change_password'), '/accounts/change_password/')

    def test_accounts_urls__change_password__done(self):
        self.assertEqual(reverse('accounts:change_password_done'), '/accounts/change_password/done/')

    def test_accounts_urls__urls(self):
        self.assertEqual(reverse('accounts:urls'), '/accounts/urls/')

    def test_accounts_urls__urls__add(self):
        self.assertEqual(reverse('accounts:urls_add'), '/accounts/urls/add/')

    def test_accounts_urls__urls__detail(self):
        self.assertEqual(reverse('accounts:urls_detail', args=(1,)), '/accounts/urls/1/detail/')

    def test_accounts_urls__urls__change(self):
        self.assertEqual(reverse('accounts:urls_change', args=(1,)), '/accounts/urls/1/change/')