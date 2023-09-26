from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from recipe.serializers import TagSerializer
from core.models import Tag

TAGS_LIST_URL=reverse('recipe:tag-list')


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
        