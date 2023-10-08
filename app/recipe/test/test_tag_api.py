from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from recipe.serializers import TagSerializer
from core.models import Tag, Recipe
from decimal import Decimal

TAGS_LIST_URL=reverse('recipe:tag-list')

def get_tag_detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id,])
class PublicTagApiTest(TestCase):
    """testing tag api while user is not authorized."""

    def setUp(self):
        self.client=APIClient()

    def test_get_tag_list(self):
        """getting tags list"""
        response= self.client.get(TAGS_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagApiTest(TestCase):
    """test tag api requesting with authorized user"""

    def setUp(self):
        self.client=APIClient()

        self.user=get_user_model().objects.create(
            email='testuser@test.com',
            password='testuserspass',
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_get_tag_list(self):
        """test getting tags list"""

        Tag.objects.create(user=self.user, name='tag1')
        Tag.objects.create(user=self.user, name='tag2')
        Tag.objects.create(user=self.user, name='tag3')
        response = self.client.get(TAGS_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer=TagSerializer(Tag.objects.all(), many=True)
        tags_list=serializer.data

        self.assertEqual(response.data, tags_list)

    def test_tag_limited_user(self):
        """testing that tag list will return the authenticated users tags."""

        user2 = get_user_model().objects.create(
            email='seond@user.com',
            password='seconduser',
            )
        
        Tag.objects.create(user=user2, name='tag1')
        Tag.objects.create(user=self.user, name='tag2')
        Tag.objects.create(user=self.user, name='tag3')

        response = self.client.get(TAGS_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer=TagSerializer(Tag.objects.filter(user=self.user), many=True)
        tags_list=serializer.data

        self.assertEqual(response.data, tags_list)
        
    def test_update_tag(self):
        """test updating created tag object"""

        tag = Tag.objects.create(user=self.user, name='test')
        payload={
            'name':'tag',
        }

        url = get_tag_detail_url(tag.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])
    
    def test_update_another_users_tag(self):
        """testing that updating another users tag will faile."""
        user2 = get_user_model().objects.create(
            email='seond@user.com',
            password='seconduser',
            )
        
        tag = Tag.objects.create(user=user2, name='tag1')

        payload={
            'name':'new name',
        }
        
        url = get_tag_detail_url(tag.id)

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_update_tags_user(self):
    #     """testing that updating tags user is not allowed"""

    #     user2 = get_user_model().objects.create(
    #         email='seond@user.com',
    #         password='seconduser',
    #         )
        
    #     tag = Tag.objects.create(user=self.user, name='tag1')

    #     payload={
    #         'user':user2,
    #     }
        
    #     url = get_tag_detail_url(tag.id)

    #     response = self.client.patch(url, payload)

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_tag(self):
        """test deleting tag api"""

        tag = Tag.objects.create(user=self.user, name='tag1')

        
        url = get_tag_detail_url(tag.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_delete_another_users_tag(self):
        """test deleting another users tag tag api"""

        user2 = get_user_model().objects.create(
            email='seond@user.com',
            password='seconduser',
            )
        
        tag = Tag.objects.create(user=user2, name='tag1')

        
        url = get_tag_detail_url(tag.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(Tag.objects.filter(id=tag.id).exists())

    
    def test_get_assigned_only_tags(self):
        """test getting tags those are assigned to a recipe"""

        tag1=Tag.objects.create(user=self.user, name='tag1')
        tag2=Tag.objects.create(user=self.user, name='tag2')

        recipe=Recipe.objects.create(
            title='new recipe',
            time_minute=5,
            price=Decimal('9.02'),
            user=self.user,
        )

        recipe.tags.add(tag1)
        payload={'assigned_only':True}

        response=self.client.get(TAGS_LIST_URL, payload)

        ser1=TagSerializer(tag1)
        ser2=TagSerializer(tag2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ser1.data, response.data)
        self.assertNotIn(ser2.data, response.data)


    def test_assigned_only_list_is_unique(self):
        """testing that assigned only ingredients are unique in list."""

        tag1=Tag.objects.create(user=self.user, name='tag1')
        tag2=Tag.objects.create(user=self.user, name='tag2')

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

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)
        payload={'assigned_only':True}

        response=self.client.get(TAGS_LIST_URL, payload)


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))