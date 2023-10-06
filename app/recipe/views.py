"""api endpoints for recipe api"""


from rest_framework import viewsets, mixins, status
from .serializers import RecipeSerializer, RecipeDetailSerializer, TagSerializer, IngredientSerializer, RecipeImageSerializer
from core.models import Recipe, Tag, Ingredient
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

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
        elif self.action=='upload_image':
            return RecipeImageSerializer

        return self.serializer_class
    
    def perform_create(self, serializer):
        """set the authenticated user to the created recipe object"""
        serializer.save(user=self.request.user)
    
    @action(methods=['POST',], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        recipe=self.get_object()

        serializer=self.get_serializer(recipe, request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class BaseRecipaAttrView(mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                           mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    """base manager api view for recipe objects attributes."""
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        """returns queryset for the authenticated user."""
        return self.queryset.filter(user=self.request.user)
    

class TagView(BaseRecipaAttrView):
    """the manager api view for tag api."""

    serializer_class = TagSerializer
    queryset=Tag.objects.all()

class IngredientView(BaseRecipaAttrView):
    """manager view for ingredient"""

    serializer_class=IngredientSerializer
    queryset=Ingredient.objects.all()
    
    