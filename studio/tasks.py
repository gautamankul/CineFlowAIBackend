
from celery import shared_task

from .ai.editor import assemble
from .ai.image_model import generate_image
from .ai.text_model import make_storyboard
from .ai.video_model import generate_clip
from .models import Project, Scene


@shared_task
def generate_storyboard_task(project_id, scene_count):
    project = Project.objects.get(pk=project_id)

    project.scenes.all().delete()

    storyboard = make_storyboard(
        project.prompt,
        project.style,
        scene_count,
    )

    for index, scene_data in enumerate(storyboard, start=1):
        Scene.objects.create(
            project=project,
            scene_number=index,
            **scene_data,
        )

    project.status = "storyboard_generated"
    project.save()


@shared_task
def generate_scene_task(scene_id):
    scene = Scene.objects.get(pk=scene_id)

    try:
        scene.status = "generating_image"
        scene.save()

        scene.reference_image.name = generate_image(scene)

        scene.status = "generating_video"
        scene.save()

        scene.video.name = generate_clip(scene)

        scene.status = "completed"

    except Exception as error:
        scene.status = "failed"
        scene.error_message = str(error)

    finally:
        scene.save()


@shared_task
def assemble_video_task(project_id):
    project = Project.objects.get(pk=project_id)

    project.final_video.name = assemble(project)
    project.status = "completed"

    project.save()
