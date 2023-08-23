import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from user.models import NewUser
from recipe.models import Tag, Ingredient, Recipe, TagRecipe, IngredientRecipe, FavoriteRecipe

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
    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        fields = ('id', 'name', 'amount','measurement_unit')
        model = IngredientRecipe


class IngredientRecipeCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeListRetrieveSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    author = NewUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'text', 
                  'tags', 'ingredients', 
                  'image', 
                  'cooking_time', 'author', 'is_favorited')
        model = Recipe

    def get_ingredients(self, recipe) -> dict:
        queryset = IngredientRecipe.objects.filter(recipe=recipe)
        return IngredientRecipeSerializer(queryset, many=True).data
    
    def get_is_favorited(self, recipe) -> bool:
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=request.user, recipe=recipe).exists()
    

class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientRecipeCreateUpdateSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = NewUserSerializer(required=False)

    class Meta:

        fields = ('id', 'name', 'text', 
                  'tags', 'ingredients', 
                  'image', 
                  'cooking_time', 'author')
        model = Recipe


    def create(self, validated_data) -> Recipe:
        ingredients_list = validated_data.pop('ingredients')
        tags_list = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(
            author=author, **validated_data)
        recipe.save()
        for tag in tags_list:
            TagRecipe.objects.create(
            tag=tag, recipe=recipe)
        for ingredient in ingredients_list:
            IngredientRecipe.objects.create(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=recipe,  
            )
        recipe.is_favorited = False
        return recipe

    def update(self, instance, validated_data) -> Recipe:
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        tags_list = validated_data.pop('tags')
        ingredients_list= validated_data.pop('ingredients')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        TagRecipe.objects.filter(recipe=instance).delete()
        for tag in tags_list:
            TagRecipe.objects.create(
                tag=tag, recipe=instance)
        for edit_ingredient in ingredients_list:
            IngredientRecipe.objects.create(
                ingredient=edit_ingredient['id'],
                recipe=instance,
                amount=edit_ingredient['amount']
            )
        instance.is_favorited = instance.is_favorited
        instance.save()
        return instance

    def to_representation(self, instance) -> dict:
        context = {'request': self.context.get('request')}
        return RecipeListRetrieveSerializer(instance, context=context).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'image', 'name', 'cooking_time')
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return FavoriteRecipeSerializer(instance, context=context).data