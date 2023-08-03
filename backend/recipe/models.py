from django.contrib.auth import get_user_model
from django.db import models
from user.models import NewUser


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7, null=True, blank=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self) -> str:
        return str(self.name)


class Ingredient(models.Model):
    name = models.CharField(max_length=200, null=True, blank=False)
    measurement_unit = models.CharField(max_length=200, null=True, blank=False)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
    
    def __str__(self) -> str:
        return str(self.name)
    

class Recipe(models.Model):
    ingredients = models.ManyToManyField(Ingredient, blank=False, through='IngredientRecipe')
    tags = models.ManyToManyField(Tag, blank=False, through='TagRecipe')
    image = models.ImageField(null=True, blank=True, upload_to='recipe_image/')
    name = models.CharField(max_length=200, null=True, blank=False)
    text = models.TextField(null=True, blank=False)
    cooking_time = models.PositiveIntegerField(null=True, blank=False)
    author = models.ForeignKey(NewUser, on_delete=models.CASCADE, null=True, blank=False)

    class Meta:
        ordering = ['name']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self) -> str:
        return str(self.name)


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, null=True, blank=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=False)
    amount = models.IntegerField(null=True, blank=False)

    class Meta:
        ordering = ['ingredient','recipe']
        verbose_name = 'Ingredient Recipe'
        verbose_name_plural = 'Ingredient Recipes'

    def __str__(self) -> str:
        return str(self.amount)


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True, blank=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=False)

    class Meta:
        ordering = ['tag','recipe']
        verbose_name = 'Tag Recipe'
        verbose_name_plural = 'Tag Recipes'
    
    def __str__(self) -> str:
        return str(self.tag)