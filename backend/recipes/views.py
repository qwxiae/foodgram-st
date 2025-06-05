from django.shortcuts import get_object_or_404, redirect

from recipes.models import Recipe


def redirect_to_full_recipe(request, short_url):
    recipe = get_object_or_404(Recipe, short_url=short_url)
    return redirect(f"/recipes/{recipe.id}")
