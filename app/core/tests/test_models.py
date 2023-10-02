"""testing models"""


from django.contrib.auth import get_user_model
from django.test import TestCase
from decimal import Decimal
from core.models import Recipe, Tag, Ingredient

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

    def test_create_superuser(self):
        email = 'superUser@email.com'
        password = 'superuserpass'

        user = get_user_model().objects.create_superuser(email,password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


    def test_create_recipe(self):
        user = get_user_model().objects.create(
            email='email@email.com',
            name='emailuser',
            password='useremail',
        )

        recipe = Recipe.objects.create(
            user=user,
            title='testing recipe',
            price=Decimal('99.80'),
            time_minute=12,
            description='recipe description'
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        user = get_user_model().objects.create(
            email='email@email.com',
            name='emailuser',
            password='useremail',
        )

        tag = Tag.objects.create(user=user, name='testTag')

        self.assertTrue(Tag.objects.filter(id=tag.id).exists())
        self.assertEqual(tag.user, user)
        self.assertEqual(str(tag), tag.name)


    def test_create_ingredient(self):
        """test creating new Ingredient"""

        user=get_user_model().objects.create(
            email='test@test.com',
            password='testpassword',
        )

        Ingredient.objects.create(
            user=user,
            name='ingredient'
        )

        exists=Ingredient.objects.filter(
            user=user,
            name='ingredient',
        ).exists()

        self.assertTrue(exists)