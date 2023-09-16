"""test cases for admin of the site"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class TestAdmin(TestCase):

    def setUp(self):
        """initializing requirements of testing"""

        self.client = Client()
        self.superuser = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='admin',
        )

        self.client.force_login(self.superuser)
        self.user = get_user_model().objects.create(
            email='user@example.com',
            password='user',
            name="user",
        )

    def test_users_list(self):
        """getting users list and testing that"""

        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)


    def test_update_user(self):
        """checking that update user page works"""

        url = reverse('admin:core_user_change', args=[self.user.id])

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)