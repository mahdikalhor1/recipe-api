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

        self._get_or_create_tags(tags, recipe)
        
        return recipe
    
    def update(self, instance, validated_data):
        """updating recipe object"""
        tags = validated_data.pop('tags', None)


        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        
        return instance
        
    def _get_or_create_tags(self, tags, instance):
        """create and adding tags to the instances tag list"""

        user = self.context['request'].user

        for tag in tags:
            tag_obj, created=Tag.objects.get_or_create(user=user, **tag)
            instance.tags.add(tag_obj)




class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

