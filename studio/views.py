from rest_framework import decorators, response, status, viewsets
from .models import Character, Project, Scene
from .serializers import (CharacterSerializer, ProjectSerializer, SceneSerializer, )
from .tasks import (assemble_video_task, generate_scene_task, generate_storyboard_task, )


# Create views here.
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-updated_at")
    serializer_class = ProjectSerializer

    @decorators.action(detail=True, methods=["post"])
    def storyboard(self, request, pk=None):
        scene_count = int(request.data.get("scene_count", 3))
        generate_storyboard_task.delay(str(pk),scene_count,)
        return response.Response({"queued": True},status=status.HTTP_202_ACCEPTED,)

    @decorators.action(detail=True, methods=["post"])
    def generate_all(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        for scene in project.scenes.all():
            generate_scene_task.delay(scene.id)
        return response.Response({"queued": True},status=status.HTTP_202_ACCEPTED,)

    @decorators.action(detail=True, methods=["post"])
    def assemble(self, request, pk=None):
        assemble_video_task.delay(str(pk))

        return response.Response(
            {"queued": True},
            status=status.HTTP_202_ACCEPTED,
        )


class SceneViewSet(viewsets.ModelViewSet):
    queryset = Scene.objects.all()
    serializer_class = SceneSerializer

    @decorators.action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        generate_scene_task.delay(pk)

        return response.Response(
            {"queued": True},
            status=status.HTTP_202_ACCEPTED,
        )


class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
