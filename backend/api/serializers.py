from rest_framework import serializers, status, validators

from api.fields import Base64ImageField
from recipe.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                           Recipe, ShoppingRecipe, Tag, TagRecipe)
from user.models import NewUser, Subscription


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
            user.is_authenticated
            and user.subscription_set.filter(
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


class RecipeListRetrieveSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    author = NewUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    ingredients = IngredientRecipeSerializer(source='ingredientrecipe_set',
                                             many=True,
                                             read_only=True)

    class Meta:
        fields = ('id', 'name', 'text',
                  'tags', 'ingredients',
                  'image',
                  'cooking_time', 'author',
                  'is_favorited', 'is_in_shopping_cart')
        model = Recipe

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

    def validate(self, data):
        ingredients_list = data['ingredients']
        ingredients_list_validate = []
        for ingredient in ingredients_list:
            amount = ingredient['amount']
            if amount <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть натуральным числом',
                )
            ingredients_list_validate.append(ingredient.get('id'))
            if len(set(ingredients_list_validate)
                   ) != len(ingredients_list_validate):
                raise serializers.ValidationError(
                    'Нельзя дублировать ингредиенты в рецепте',
                )
        return data

    def create_ingredients_tags(self, recipe,
                                ingredients_list, tags_list):
        tags = []
        for tag in tags_list:
            TagRecipe(tag=tag, recipe=recipe)
        TagRecipe.objects.bulk_create(tags)
        ingredients = []
        for ingredient in ingredients_list:
            amount = ingredient['amount']
            ingredients.append(
                IngredientRecipe
                (ingredient=ingredient['id'],
                 amount=amount,
                 recipe=recipe,))
        IngredientRecipe.objects.bulk_create(ingredients)

    def create(self, validated_data) -> Recipe:
        ingredients_list = validated_data.pop('ingredients')
        tags_list = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(
            author=author, **validated_data)
        self.create_ingredients_tags(recipe, ingredients_list,
                                     tags_list)
        return recipe

    def update(self, instance, validated_data) -> Recipe:
        tags_list = validated_data.pop('tags')
        ingredients_list = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients_tags(instance, ingredients_list,
                                     tags_list)
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

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'error': f'Вы уже добавили рецепт {recipe.name} в избранное'},
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeReturnSerializer(instance.recipe, context=context).data


class ShoppingRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingRecipe
        fields = ['user', 'recipe']

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if ShoppingRecipe.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'error': f'Вы уже добавили рецепт {recipe.name} в список'},
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeReturnSerializer(instance.recipe, context=context).data


class SubscribeReturnSerializer(NewUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = NewUser
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes',
                  'recipes_count')

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
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('subscriber', 'subscribe'),
                message='Такая подписка уже существует'
            )
        ]

    def validate(self, data):
        subscriber = data['subscriber']
        subscribe = data['subscribe']
        if subscriber == subscribe:
            raise serializers.ValidationError(
                {
                    'error':
                    f'Пользователь {subscriber} подписывается на самого себя'
                }
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeReturnSerializer(
            instance.subscribe,
            context={'request': request},
        ).data
