from rest_framework import generics, authentication, permissions
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

class ManageUserApi(generics.RetrieveUpdateAPIView):
    """api view for updating and getting authenticated users info"""

    serializer_class=UserSerializer
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get_object(self):
        """returns the authenticated user"""
        return self.request.user
    
    