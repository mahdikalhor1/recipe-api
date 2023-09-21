"""unit tests for recipe api"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from core.models import Recipe
from decimal import Decimal
from rest_framework import status
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL=reverse('recipe:recipe-list')


def create_recipe(user, **params):
    default_recipe={
            'user':user,
            'title':'test',
            'time_minute':10,
            'description':'some description',
            'price':Decimal('50.20'),
            'link':'www.test.com/recipe'
        }
    
    default_recipe.update(params)
    recipe = Recipe.objects.create(**default_recipe)

    return recipe

def get_recipe_detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id,])

class PublicRecipeApiTest(TestCase):

    def setUp(self):
        self.client=APIClient()
    

    def test_get_list_unauthorized(self):
        """testing that authorization is required to get recipes"""
        response = self.client.get(RECIPES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(
            email='testuser@gmail.com',
            password='testuser',
            name='testuser'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    
    def test_get_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user, **{'title':'second'})
        create_recipe(user=self.user, **{'title':'third'})

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')

        recipes_ser=RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, recipes_ser.data)

    def test_get_current_users_recipes(self):
        second_user = get_user_model().objects.create(
            email='seconduser@email.com',
            password='seconduser',
        )

        create_recipe(user=second_user)
        create_recipe(user=second_user)
        create_recipe(user=self.user)

        current_users_recepies=Recipe.objects.filter(user=self.user).all()

        current_users_recepies_ser=RecipeSerializer(current_users_recepies, many=True)

        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, current_users_recepies_ser.data)

    def get_recipe_detail(self):
        recipe = create_recipe(user=self.user)

        url = get_recipe_detail_url(recipe.id)

        response = self.client.get(url)

        serializer= RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
    
