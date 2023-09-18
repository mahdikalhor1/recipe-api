"""tests for user api"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

CREATE_USER_URL = reverse('user:create')

class TestPublickUserApi(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """creating user with valid data"""

        payload={
            'email':'testuser@email.com',
            'password':'testuserpass',
            'name':'testuser',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = get_user_model().objects.get(email=payload['email'])

        self.assertTrue(created_user.check_password(payload['password']))

        self.assertNotIn('password', response.data)


    def test_create_user_with_same_email(self):
        "testing that creating users with same email address is not allowed"
        payload={
            'email':'testuser@email.com',
            'password':'testuserpass',
            'name':'testuser',
        }

        get_user_model().objects.create(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_user_with_short_pass(self):
        """testing that creating user with pass less than 8 characters is not allowed"""

        payload={
            'email':'testuser@email.com',
            'password':'pass123',
            'name':'testuser',
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.assertFalse(get_user_model().objects.filter(email=payload['email']).exists())

