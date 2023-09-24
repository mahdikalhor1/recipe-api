"""api endpoints for recipe api"""


from rest_framework import viewsets
from .serializers import RecipeSerializer, RecipeDetailSerializer
from core.models import Recipe
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class RecipeManageView(viewsets.ModelViewSet):
    """view for managing recipe objects"""

    serializer_class = RecipeDetailSerializer
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    queryset=Recipe.objects.all()

    def get_queryset(self):
        """return recipes queryset for authenticated user"""
        return Recipe.objects.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        
        if self.action == 'list':
            return RecipeSerializer

        return self.serializer_class
    
    def perform_create(self, serializer):
        """set the authenticated user to the created recipe object"""
        serializer.save(user=self.request.user)
