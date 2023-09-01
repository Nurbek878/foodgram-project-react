import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from user.models import NewUser, Subscription
from recipe.models import (Tag, Ingredient, Recipe, TagRecipe,
                           IngredientRecipe, FavoriteRecipe,
                           ShoppingRecipe)


class NewUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')
        model = NewUser

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        return (
            user.is_authenticated and
            user.subscription_set.filter(
                subscribe=obj
            ).exists()
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSetSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        fields = ('id', 'name', 'amount', 'measurement_unit')
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
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'text',
                  'tags', 'ingredients',
                  'image',
                  'cooking_time', 'author',
                  'is_favorited', 'is_in_shopping_cart')
        model = Recipe

    def get_ingredients(self, recipe) -> dict:
        queryset = IngredientRecipe.objects.filter(recipe=recipe)
        return IngredientRecipeSerializer(queryset, many=True).data

    def get_is_favorited(self, recipe) -> bool:
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            return FavoriteRecipe.objects.filter(user=request.user,
                                                 recipe=recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe) -> bool:
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            return ShoppingRecipe.objects.filter(user=request.user,
                                                 recipe=recipe).exists()
        return False


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
            TagRecipe.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients_list:
            IngredientRecipe.objects.create(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=recipe,
            )
        recipe.is_favorited = False
        recipe.is_in_shopping_cart = False
        return recipe

    def update(self, instance, validated_data) -> Recipe:
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        tags_list = validated_data.pop('tags')
        ingredients_list = validated_data.pop('ingredients')
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
        instance.is_in_shopping_cart = instance.is_in_shopping_cart
        instance.save()
        return instance

    def to_representation(self, instance) -> dict:
        context = {'request': self.context.get('request')}
        return RecipeListRetrieveSerializer(instance, context=context).data


class RecipeReturnSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'image', 'name', 'cooking_time')
        model = Recipe


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeReturnSerializer(instance, context=context).data


class ShoppingRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingRecipe
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeReturnSerializer(instance, context=context).data


class SubscribeReturnSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = NewUser
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes',
                  'recipes_count')

    def get_is_subscribed(self, user):
        subscribers = user.subscribed_by.all()
        if user.is_anonymous or subscribers.count() == 0:
            return False
        return Subscription.objects.filter(
            subscriber=user, subscribe=user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeReturnSerializer(
            recipes, many=True,
            context={'request': self.context.get('request')}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ['subscriber', 'subscribe']

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeReturnSerializer(
            instance.subscribe,
            context={'request': request},
        ).data
