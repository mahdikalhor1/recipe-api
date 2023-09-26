"""unit tests for recipe api"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from core.models import Recipe
from decimal import Decimal
from rest_framework import status
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from decimal import Decimal

RECIPES_URL=reverse('recipe:recipe-list')

def create_user(**params):
    return get_user_model().objects.create(**params)

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
        self.user = create_user(
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
        second_user = create_user(
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
    
    def test_create_recipe(self):
        """testing create recipe"""

        payload={
            'title':'test',
            'price': Decimal('20.32'),
            'time_minute':50,
        }

        response=self.client.post(RECIPES_URL, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe_object=Recipe.objects.get(id=response.data['id'])

        for key, value in payload.items():
            self.assertEqual(getattr(recipe_object, key), value)

        self.assertEqual(recipe_object.user, self.user)

    def test_full_update_recipe(self):
        """Testing full update of recipe object"""
        recipe = create_recipe(user=self.user)

        payload={'title':'new test',
            'time_minute':10,
            'description':'new description',
            'price':Decimal('50.20'),
            'link':'www.test.com/recipe-new-update'
        }

        url = get_recipe_detail_url(recipe_id=recipe.id)

        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertEqual(self.user, recipe.user)

        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

    
    def test_partial_update_recipe(self):
        """Testing partial update of recipe""" 

        recipe = create_recipe(user=self.user)

        payload={
            'title':'new title',
            'link':'new link',
        }

        url = get_recipe_detail_url(recipe.id)

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        self.assertEqual(self.user, recipe.user)

        for key, value in payload.items():
            self.assertEqual(value, getattr(recipe, key))
    
    def test_update_user_recipe(self):
        """Test updating recipes user is not allowed"""
        recipe = create_recipe(self.user)
        new_user= create_user(email='newuser@email.com', password='newuserspass')

        payload={
            'user':new_user,
                 }
        
        url = get_recipe_detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """test deleting a recipe objec"""
        recipe = create_recipe(self.user)

        url = get_recipe_detail_url(recipe.id)
        response=self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())


    def test_delete_another_users_recipe(self):
        """test deleting another users recipe object is not allowed"""    
        
        new_user= create_user(email='newuser@email.com', password='newuserspass')
        recipe = create_recipe(new_user)

        url = get_recipe_detail_url(recipe_id=recipe.id)

        response=self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    
        