"""serializers for recipe api"""
from rest_framework import serializers
from core.models import Recipe, Tag
class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields=['id', 'title', 'price', 'time_minute', 'link']
        read_only_fields=['id']

class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model=Tag
        fields='__all__'
        read_only=['id']


