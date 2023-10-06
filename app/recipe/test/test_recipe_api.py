"""unit tests for recipe api"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from core.models import Recipe, Tag, Ingredient
from decimal import Decimal
from rest_framework import status
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from decimal import Decimal
import os

from django.conf import settings
from PIL import Image
import tempfile


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

def get_recipe_image_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    
    def test_create_recipe_new_tags(self):
        """test crete recipe with non existing tags"""

        payload={
            'title':'new recipe',
            'time_minute': 40,
            'price': Decimal('60.03'),
            'tags':[
                {
                    'name':'tag1'
                },
                {
                    'name':'tag2'
                },

            ]
        }

        response = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        recipes=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            exists=Tag.objects.filter(
                user=self.user,
                name=tag['name'],

            ).exists()

            self.assertTrue(exists)


    def create_recipe_with_existing_tag(self):
        """testing crete recipe with existing tags"""

        existing_tag=Tag.objects.create(user=self.user,name='existing tag')
        
        payload={
            'title':'new_recipe',
            'time_minute':52,
            'price':Decimal('52.03'),
            'tags':[
                {
                    'name':'existing tag',
                }
                ,
                {
                    'name':'new tag',
                },
            ]


        }


        response=self.client.post(RECIPES_URL, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)

        recipe=recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(existing_tag, recipe.tags.all())

        for tag in payload['tags']:
            exists=Tag.objects.filter(
                user=self.user,
                name=tag['name'],
                ).exists()
            self.assertTrue(exists)


    def test_add_tag_to_recipe(self):
        """test adding new tag to recipes tag list."""
        recipe = create_recipe(self.user,
                               **{'title':'new_recipe',}
                               )

        tag=Tag.objects.create(user=self.user, name='tag')
        tag1=Tag.objects.create(user=self.user, name='tag1')
        tag2=Tag.objects.create(user=self.user, name='tag2')

        payload={
            'tags':[
                {
                    'name':'tag',
                }
                ,
                {
                    'name':'tag1',
                },
                {
                    'name':'tag2',
                },
            ]
        }
        
        url = get_recipe_detail_url(recipe.id)
        response=self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(recipe.tags.count(), 3)


        self.assertIn(tag, recipe.tags.all())
        self.assertIn(tag1, recipe.tags.all())
        self.assertIn(tag2, recipe.tags.all())


    def test_delete_tag_from_recipe(self):
        """test deleting tag object from recipe"""
        recipe = create_recipe(self.user,
                               **{'title':'new_recipe',}
                               )

        tag = Tag.objects.create(user=self.user, name='tag')
        tag1 = Tag.objects.create(user=self.user, name='tag1')
        tag2 = Tag.objects.create(user=self.user, name='tag2')

        recipe.tags.add(tag)
        recipe.tags.add(tag1)
        recipe.tags.add(tag2)

        payload={
            'tags':[
                {
                    'name':'tag1',
                },
                {
                    'name':'tag2',
                },
            ]
        }
        
        url = get_recipe_detail_url(recipe.id)
        response=self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 2)


        self.assertNotIn(tag, recipe.tags.all())
        self.assertIn(tag1, recipe.tags.all())
        self.assertIn(tag2, recipe.tags.all())


    def test_clear_recipes_tags(self):
        """test cleat recipes tags list"""
        recipe = create_recipe(self.user)

        tag = Tag.objects.create(user=self.user, name='tag')
        tag1 = Tag.objects.create(user=self.user, name='tag1')
        tag2 = Tag.objects.create(user=self.user, name='tag2')

        recipe.tags.add(tag)
        recipe.tags.add(tag1)
        recipe.tags.add(tag2)

        payload={
            'tags':[]
        }
        
        url = get_recipe_detail_url(recipe.id)
        response=self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)


        self.assertNotIn(tag, recipe.tags.all())
        self.assertNotIn(tag1, recipe.tags.all())
        self.assertNotIn(tag2, recipe.tags.all())

    def test_create_tag_when_updating(self):
        """test creating tag objects via recipes update api."""
        recipe = create_recipe(user=self.user)


        payload={
            'tags':[
                {
                    'name':'new tag',
                },
                {
                    'name':'created tag',
                },
            ]
        }


        url=get_recipe_detail_url(recipe.id)

        response=self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            exists=Tag.objects.filter(
                user=self.user,
                name=tag['name']
            ).exists()

            self.assertTrue(exists)

    def test_create_ingredient_on_update_recipe(self):
        
        recipe=create_recipe(user=self.user)
        payload={
            'ingredients':[
                {'name':'new ingredient',},
                {'name':'test',},
            ]
        }

        url=get_recipe_detail_url(recipe.id)
        response=self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(recipe.ingredients.count(), 2)
        
        for ingredient in payload['ingredients']:
            ingredient=Ingredient.objects.get(
                user=self.user,
                name=ingredient['name'],
                )
            self.assertIn(ingredient, recipe.ingredients.all())

    def test_add_existing_ingredient_to_recipe(self):
        """test adding existing ingredient object to recipe"""

        ingredient=Ingredient.objects.create(user=self.user, name='new ing')

        recipe=create_recipe(user=self.user)

        payload={
            'ingredients':[{
                'name':'new ing',
            },],
        }

        url=get_recipe_detail_url(recipe.id)
        response=self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient, recipe.ingredients.all())
        self.assertEqual(recipe.ingredients.count(), 1)

    def test_clear_ingredient_list(self):
        """test cleat all ingredient obj of recipe"""

        ingredient=Ingredient.objects.create(user=self.user, name='new ing')

        recipe=create_recipe(user=self.user)

        recipe.ingredients.add(ingredient)

        payload={
            'ingredients':[],
        }

        url=get_recipe_detail_url(recipe.id)
        response=self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(ingredient, recipe.ingredients.all())
        self.assertEqual(recipe.ingredients.count(), 0)
    
    def test_create_ingredient_on_create_recipe(self):
        """test creating ingredient object throgh create recipe object."""

        payload={
            'title':'new_recipe',
            'time_minute':52,
            'price':Decimal('52.03'),
            'ingredients':[
                {
                    'name':'existing ing',
                }
                ,
                {
                    'name':'new ing',
                },
            ]
        }

        response=self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe=Recipe.objects.get(id=response.data['id'])

        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            ingredient_obj=Ingredient.objects.get(
                user=self.user,
                name=ingredient['name'],
            )        
            
            self.assertIn(ingredient_obj, recipe.ingredients.all())
        

    def test_create_recipe_with_existing_ingredients(self):
        """test creating new recipe obj with existing ingredient obj."""

        ingredient=Ingredient.objects.create(user=self.user,name='existing ing')
        payload={
            'title':'new_recipe',
            'time_minute':52,
            'price':Decimal('52.03'),
            'ingredients':[
                {
                    'name':'existing ing',
                }
            ]
        }

        response=self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe=Recipe.objects.get(id=response.data['id'])

        self.assertEqual(recipe.ingredients.count(), 1)      
            
        self.assertIn(ingredient, recipe.ingredients.all())

    
class ImageApiTest(TestCase):
    """testing api for recipes image."""

    def setUp(self):
        self.user=get_user_model().objects.create(
            email='selfuser@self.dd',
            password='selfuser',
        )

        self.client=APIClient()
        self.client.force_authenticate(user=self.user)
        self.recipe=create_recipe(user=self.user)

    def dearDown(self):
        self.recipe.image.delete()

    
    def test_upload_image(self):
        """test uploading image to recipe."""

        url=get_recipe_image_url(self.recipe.id)

        # file_path=os.path.join(settings.BASE_DIR, 'recipe/test/testimg/14236.jpg')
        
        # file=open(file_path, encoding='utf-8')
        # image= Image.open(file_path)
        
        # image= Image.frombytes(file.read())

        with tempfile.NamedTemporaryFile(suffix='.jpg') as file:
            image = Image.new('RGB', (28,28))
            image.save(file, format='JPEG')
            file.seek(0)
            payload={'image':file}
            response=self.client.post(url, payload, format='multipart')
       
       
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('image', response.data)

        self.recipe.refresh_from_db()

        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_bad_data(self):
        """test uploading invalid data for image file."""

        url=get_recipe_image_url(self.recipe.id)
        payload={'image':'invalid image file!'}

        response=self.client.post(url, payload, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



        