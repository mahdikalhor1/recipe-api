"""unit tests for ingredient api endpoints"""

from core.models import Ingredient
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from recipe.serializers import IngredientSerializer

INGREDIENTS_LIST_URL=reverse('recipe:ingredient-list')

class TestPublicIngredientApi(TestCase):
    """test sending unauthorized request to ingredients api."""

    def test_get_list(self):
        """test getting list of objects will faile with unauthorized request"""
        client=APIClient()

        response=client.get(INGREDIENTS_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class TestPrivateIngredientApi(TestCase):
    """test sending authorized requests to ingredients api."""
    
    def setUp(self):
        self.user=get_user_model().objects.create(
            email='email@email.email',
            password='mypassword',
        )

        self.client=APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_get_list(self):
        """test get list of ingredient objects."""

        Ingredient.objects.create(user=self.user, name='test1')
        Ingredient.objects.create(user=self.user, name='test2')

        response=self.client.get(INGREDIENTS_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ingredients=Ingredient.objects.filter(user=self.user)
        serializer=IngredientSerializer(data=ingredients, many=True)
        serializer.is_valid()

        self.assertEqual(serializer.data, response.data)

    