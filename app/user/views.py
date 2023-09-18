from rest_framework import generics
from .serializers import UserSerializer

class CreateUserApi(generics.CreateAPIView):
    serializer_class=UserSerializer
