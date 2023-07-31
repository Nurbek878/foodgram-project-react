import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from user.models import NewUser
from recipe.models import Tag, Ingredient, Recipe, TagRecipe, IngredientRecipe

class NewUserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name')
        model = NewUser


class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSetSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name','measurement_unit')
        model = Ingredient


class IngredientRecipeSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        fields = ('id', 'name', 'amount','measurement_unit')
        model = IngredientRecipe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = NewUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('id', 'name', 'text', 
                  'tags', 'ingredients', 
                  'image', 
                  'cooking_time', 'author')
        model = Recipe

    def get_ingredients(self, obj):
        queryset = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(queryset, many=True).data

    def create(self, validated_data)-> Recipe:
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag, status_tag = Tag.objects.get_or_create(
                **tag)
            TagRecipe.objects.create(
                tag=current_tag, recipe=recipe)
            
        for ingredient in ingredients:
            current_ingredient, status_ingredient = Ingredient.objects.get_or_create(
                **ingredient)
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe)
        return recipe
    
    def update(self, instance, validated_data)-> Recipe:
        # tags = validated_data.pop('tags')
        ingredients = validated_data.get('ingredients')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        # for tag in tags:
        #     current_tag, status_tag = Tag.objects.get_or_create(
        #         **tag)
        #     TagRecipe.objects.create(
        #         tag=current_tag, recipe=instance)
            
        for ingredient in ingredients:
            current_ingredient, status_ingredient = Ingredient.objects.get_or_create(
                **ingredient)
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=instance)
        instance.save()
        return instance