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
        fields = ('measurement_unit')
        model = Ingredient


class IngredientRecipeSerializer(serializers.ModelSerializer):
    ingredient = IngredientSetSerializer()

    class Meta:
        fields = ('id', 'ingredient', 'amount',)
        model = IngredientRecipe


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = NewUserSerializer(read_only=True)

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
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.save()
