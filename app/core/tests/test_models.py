"""testing models"""


from django.contrib.auth import get_user_model
from django.test import TestCase

class TestModels(TestCase):

    
    def test_user_create_with_email(self):
        """testing creating user with email and password."""

        email='testingemail@example.com'
        password='userpassword'

        user = get_user_model().objects.create(
            email=email, password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalization(self):

        test_emails=[
            ['example@example.com', 'example@example.com'],
            ['Example@example.COM', 'Example@example.com'],
            ['EXAMPLE@example.com', 'EXAMPLE@example.com'],
            ['EXAMPLE0@EXAMPLE.com', 'EXAMPLE0@example.com'],
            ['EXAMPLE00@EXAMPLE.COM', 'EXAMPLE00@example.com'],
        ]

        for email, normalized in test_emails:
            user = get_user_model().objects.create(email)

            self.assertEqual(user.email, normalized)

    def test_creating_user_with_blank_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create('')