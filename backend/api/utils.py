from django.shortcuts import get_object_or_404
from rest_framework import response, status

from recipe.models import Recipe


def create_favorite_shopping(request, serializer, pk):
    user = request.user
    serializer = serializer(
        data={'user': user.id, 'recipe': pk},
        context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return response.Response(serializer.data,
                             status=status.HTTP_201_CREATED)


def delete_favorite_shopping(request, model, pk,
                             mes_text_del, mes_text_no):
    user = request.user
    recipe = get_object_or_404(Recipe, id=pk)
    model_for_delete = model.objects.filter(user=user, recipe=recipe)
    if model_for_delete.exists():
        model_for_delete.delete()
        return response.Response(
            f'Рецепт {recipe.name} удален из {mes_text_del}',
            status=status.HTTP_204_NO_CONTENT)
    return response.Response(
        f'Рецепта {recipe.name} не было в {mes_text_no}',
        status=status.HTTP_400_BAD_REQUEST)
