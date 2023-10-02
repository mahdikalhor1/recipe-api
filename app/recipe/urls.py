from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name='recipe'

router = DefaultRouter()

router.register('recipes', views.RecipeManageView)
router.register('tags', views.TagView, basename='tag')
router.register('ingredients', views.IngredientView, basename='ingredient')

urlpatterns=[
    path('', include(router.urls)),
]