"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)


class TagSerializer(serializers.ModelSerializer):
    """ Serializer for tags. """
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """ Serializer for ingredient. """
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for recipes. """
    tag = TagSerializer(many=True, required=False)
    ingredient = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price',
                  'link', 'tag', 'ingredient']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """ Handle getting or creating tags as needed. """
        auth_user = self.context['request'].user
        for tags in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tags,
            )
            recipe.tag.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """ Handle getting or creating ingredients as needed. """
        auth_user = self.context['request'].user
        for ingredients in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredients,
            )
            recipe.ingredient.add(ingredient_obj)

    def create(self, validated_data):
        """ Create a recipe. """
        tags = validated_data.pop('tag', [])
        ingredients = validated_data.pop('ingredient', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """ Update recipe. """
        tags = validated_data.pop('tag', [])
        ingredients = validated_data.pop('ingredient', [])
        if tags is not None:
            instance.tag.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredient.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """ Serializer for recipe detail view. """
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
