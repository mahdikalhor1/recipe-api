"""serializers for recipe api"""
from rest_framework import serializers
from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model=Tag
        fields=['name']
        read_only=['id']




class RecipeSerializer(serializers.ModelSerializer):

    tags=TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields=['id', 'title', 'price', 'time_minute', 'link', 'tags']
        read_only_fields=['id']

    def create(self, validated_data):
        """create recipe"""
        tags = validated_data.pop('tags', [])

        recipe=Recipe.objects.create(**validated_data)

        user = self.context['request'].user

        for tag in tags:
            tag_object, created=Tag.objects.get_or_create(user=user ,**tag)
            recipe.tags.add(tag_object)
        
        return recipe
        

class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

