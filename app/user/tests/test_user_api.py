"""tests for user api"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
MYACCOUNT_URL = reverse('user:myaccount')

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


    def test_create_token(self):
        """testing creation of token for valid user data"""
        user_params={
            'email':'exampleuser@gmail.com',
            'password':'exampleuser',
            'name':'example',
        }

        payload = {
            'email':'exampleuser@gmail.com',
            'password':'exampleuser',
        }

        get_user_model().objects.create(**user_params)

        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_create_token_invalid_pass(self):
        """test that creation of token will falies for invalid user password"""

        user_params={
            'email':'exampleuser@gmail.com',
            'password':'exampleuser',
            'name':'example',
        }

        payload = {
            'email':'exampleuser@gmail.com',
            'password':'invalidpass',
        }

        get_user_model().objects.create(**user_params)

        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)
    
    def test_create_token_empty_pass(self):
        """test to create token when using empty pass"""

        payload = {
            'email':'exampleuser@gmail.com',
            'password':'',
        }

        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    
    def test_get_myaccount_unauthorized(self):
        """testing that getting profile is not allowed is unauthenticated case"""

        response = self.client.get(MYACCOUNT_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class TestPrivateUserApi(TestCase):
    """testing authenticated users actions"""

    def setUp(self):
        self.user = get_user_model().create(
            email='testuser',
            password='testingpass',
            name='testuser'
        )

        self.client = APIClient

        self.client.force_authentication(user=self.user)

    
    def test_get_profile(self):
        """getting users profile"""

        response = self.client.get(MYACCOUNT_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, {
            'email':self.user.email,
            'name':self.user.name,
        })

    
    def test_post_myaccount_not_allowed(self):
        """testing that post method to myaccoutn url failes"""

        response = self.client.post(MYACCOUNT_URL, {})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        updated_data={
            'name':'newname',
            'password':'newpassword',
        }

        response = self.client.patch(MYACCOUNT_URL, updated_data)

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, updated_data['name'])
        self.assertTrue(self.user.check_password(updated_data['password']))
