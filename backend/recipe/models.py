from django.db import models

from user.models import NewUser


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя тега')
    color = models.CharField(max_length=7, null=True, blank=True,
                             verbose_name='Цвет тега')
    slug = models.SlugField(max_length=200, unique=True,
                            verbose_name='Слаг тега')

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self) -> str:
        return str(self.name)


class Ingredient(models.Model):
    name = models.CharField(max_length=200, null=True, blank=False,
                            verbose_name='Имя ингредиента')
    measurement_unit = models.CharField(max_length=200, null=True, blank=False,
                                        verbose_name='Единица измерения')

    class Meta:
        ordering = ['name']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self) -> str:
        return str(self.name)


class Recipe(models.Model):
    ingredients = models.ManyToManyField(Ingredient, blank=False,
                                         through='IngredientRecipe',
                                         verbose_name='Ингредиент')
    tags = models.ManyToManyField(Tag, blank=False, through='TagRecipe',
                                  verbose_name='Тег')
    image = models.ImageField(null=True, blank=True, upload_to='recipe_image/',
                              verbose_name='Изображение')
    name = models.CharField(max_length=200, null=True, blank=False,
                            verbose_name='Имя')
    text = models.TextField(null=True, blank=False,
                            verbose_name='Текст')
    cooking_time = models.PositiveIntegerField(null=True, blank=False,
                                               verbose_name='Время')
    author = models.ForeignKey(NewUser, on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='recipes',
                               null=True, blank=False)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self) -> str:
        return str(self.name)


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   null=True, blank=False,
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               null=True, blank=False,
                               verbose_name='Рецепт')
    amount = models.IntegerField(null=True, blank=False,
                                 verbose_name='Количество')

    class Meta:
        ordering = ['ingredient', 'recipe']
        verbose_name = 'Ingredient Recipe'
        verbose_name_plural = 'Ingredient Recipes'
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredient_recipe')]

    def __str__(self) -> str:
        return str(self.amount)


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            null=True, blank=False,
                            verbose_name='Тег')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               null=True, blank=False,
                               verbose_name='Рецепт')

    class Meta:
        ordering = ['tag', 'recipe']
        verbose_name = 'Tag Recipe'
        verbose_name_plural = 'Tag Recipes'
        constraints = [
            models.UniqueConstraint(fields=['tag', 'recipe'],
                                    name='unique_tag_recipe')]

    def __str__(self) -> str:
        return str(self.tag)


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorite_recipe',
                               null=True, blank=False,
                               verbose_name='Рецепт')
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE,
                             related_name='favorite_user',
                             null=True, blank=False,
                             verbose_name='Пользователь')

    class Meta:
        ordering = ['recipe', 'user']
        verbose_name = 'Favorite Recipe'
        verbose_name_plural = 'Favorite Recipes'
        constraints = [models.UniqueConstraint(fields=['recipe', 'user'],
                       name='unique_favorite_recipe')]


class ShoppingRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_recipe',
                               null=True, blank=False,
                               verbose_name='Рецепт')
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE,
                             related_name='shopping_user',
                             null=True, blank=False,
                             verbose_name='Пользователь')

    class Meta:
        ordering = ['recipe', 'user']
        verbose_name = 'Shopping Recipe'
        verbose_name_plural = 'Shopping Recipes'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'user'],
                                    name='unique_shopping_recipe')]
