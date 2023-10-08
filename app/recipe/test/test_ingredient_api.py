"""unit tests for ingredient api endpoints"""

from core.models import Ingredient, Recipe
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from recipe.serializers import IngredientSerializer
from decimal import Decimal

INGREDIENTS_LIST_URL=reverse('recipe:ingredient-list')

def get_ingredients_detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id,])

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

    def test_ingredient_limited_to_user(self):
        """testing that getting ingredients list returns authenticated users ingredients."""

        new_user=get_user_model().objects.create(
            email='newuser@new.new',
            password='newpassword',
            )
        
        Ingredient.objects.create(user=new_user, name='ing')
        Ingredient.objects.create(user=self.user, name='this users obj')

        response=self.client.get(INGREDIENTS_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ingredients=Ingredient.objects.filter(user=self.user)

        serializer=IngredientSerializer(data=ingredients, many=True)
        
        serializer.is_valid()

        self.assertEqual(serializer.data, response.data)


    def test_update_ingredient(self):
        """testing update ingredient object."""
        ingredient=Ingredient.objects.create(user=self.user, name='old name')

        payload={
            'name':'new name',
        }

        url=get_ingredients_detail_url(ingredient_id=ingredient.id)

        response=self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()

        self.assertEqual(ingredient.name, payload['name'])

    def test_update_another_users_obj(self):
        """test updating another users ingredient object."""
        
        new_user=get_user_model().objects.create(
            email='newuser@new.new',
            password='newpassword',
            )
        
        ingredient=Ingredient.objects.create(user=new_user, name='ing')

        payload={
            'name':'new name',
        }

        url=get_ingredients_detail_url(ingredient.id)

        response=self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_obj(self):
        """testing delete ingredient object."""
        ingredient=Ingredient.objects.create(user=self.user, name='old name')


        url=get_ingredients_detail_url(ingredient_id=ingredient.id)

        response=self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        
        self.assertFalse(
            Ingredient.objects.filter(user=self.user, name='old name').exists()
        )

    def test_delete_another_users_obj(self):
        """test deleting another users ingredient object."""
        
        new_user=get_user_model().objects.create(
            email='newuser@new.new',
            password='newpassword',
            )
        
        ingredient=Ingredient.objects.create(user=new_user, name='ing')

        url=get_ingredients_detail_url(ingredient.id)

        response=self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_assigned_only_ingredients(self):
        """test getting ingredientss those are assigned to a recipe"""

        ing1=Ingredient.objects.create(user=self.user, name='ing1')
        ing2=Ingredient.objects.create(user=self.user, name='ing2')

        recipe=Recipe.objects.create(
            title='new recipe',
            time_minute=5,
            price=Decimal('9.02'),
            user=self.user,
        )

        recipe.ingredients.add(ing1)
        payload={'assigned_only':True}

        response=self.client.get(INGREDIENTS_LIST_URL, payload)

        ser1=IngredientSerializer(ing1)
        ser2=IngredientSerializer(ing2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ser1.data, response.data)
        self.assertNotIn(ser2.data, response.data)


    def test_assigned_only_list_is_unique(self):
        """testing that assigned only ingredients are unique in list."""

        ing1=Ingredient.objects.create(user=self.user, name='ing1')
        ing2=Ingredient.objects.create(user=self.user, name='ing2')

        recipe1=Recipe.objects.create(
            title='new recipe',
            time_minute=5,
            price=Decimal('9.02'),
            user=self.user,
        )
        recipe2=Recipe.objects.create(
            title='second recipe',
            time_minute=5,
            price=Decimal('9.02'),
            user=self.user,
        )

        recipe1.ingredients.add(ing1)
        recipe2.ingredients.add(ing1)
        payload={'assigned_only':True}

        response=self.client.get(INGREDIENTS_LIST_URL, payload)


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))

    