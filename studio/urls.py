from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, SceneViewSet ,CharacterViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet)
router.register("scenes", SceneViewSet)
router.register("characters", CharacterViewSet)

urlpatterns = [
    path('', include(router.urls)),
]