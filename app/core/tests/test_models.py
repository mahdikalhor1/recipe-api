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