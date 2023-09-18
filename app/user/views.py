from rest_framework import generics
from .serializers import UserSerializer, TokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
class CreateUserApi(generics.CreateAPIView):
    """creating user api endpoint"""
    serializer_class=UserSerializer

class CreateAuthTokenApi(ObtainAuthToken):
    """creates auth token for user"""
    serializer_class=TokenSerializer
    renderer_classes=api_settings.DEFAULT_RENDERER_CLASSES