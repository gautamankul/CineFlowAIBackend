from celery import shared_task
from .ai.text_model import make_storyboard
from .ai.image_model import generate_image
from .ai.video_model import generate_clip
from .ai.editor import assemble
from .models import Project, Scene
import logging

# Initialize logger
logger = logging.getLogger(__name__)


@shared_task
def generate_storyboard_task(project_id, scene_count):
    logger.info(
        "Starting storyboard generation | Project ID: %s",
        project_id
    )

    try:
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

        logger.info(
            "Storyboard generated successfully | Project ID: %s | Scenes: %s",
            project_id,
            len(storyboard)
        )

        return {
            "status": "success",
            "project_id": str(project_id),
            "scenes_created": len(storyboard),
        }

    except Exception:
        logger.exception(
            "Storyboard generation failed | Project ID: %s",
            project_id
        )

        try:
            project = Project.objects.get(pk=project_id)
            project.status = "failed"
            project.error_message = "Storyboard generation failed."
            project.save()
        except Exception:
            logger.exception(
                "Could not update project failure status | Project ID: %s",
                project_id
            )

        raise


@shared_task
def generate_scene_task(scene_id):
    logger.info(
        "Starting scene generation | Scene ID: %s",
        scene_id
    )

    try:
        scene = Scene.objects.get(pk=scene_id)

        scene.status = "generating_image"
        scene.save()

        logger.info(
            "Generating image | Scene ID: %s",
            scene_id
        )

        scene.reference_image.name = generate_image(scene)

        logger.info(
            "Image generated successfully | Scene ID: %s",
            scene_id
        )

        scene.status = "generating_video"
        scene.save()

        logger.info(
            "Generating video | Scene ID: %s",
            scene_id
        )

        scene.video.name = generate_clip(scene)

        scene.status = "completed"
        scene.save()

        logger.info(
            "Scene completed successfully | Scene ID: %s",
            scene_id
        )

        return {
            "status": "success",
            "scene_id": scene_id,
        }

    except Exception:
        logger.exception(
            "Scene generation failed | Scene ID: %s",
            scene_id
        )

        try:
            scene = Scene.objects.get(pk=scene_id)
            scene.status = "failed"
            scene.error_message = "Scene generation failed. Check application logs."
            scene.save()
        except Exception:
            logger.exception(
                "Could not update scene failure status | Scene ID: %s",
                scene_id
            )

        raise


@shared_task
def assemble_video_task(project_id):
    logger.info(
        "Starting final video assembly | Project ID: %s",
        project_id
    )

    try:
        project = Project.objects.get(pk=project_id)

        project.final_video.name = assemble(project)
        project.status = "completed"
        project.save()

        logger.info(
            "Final video assembled successfully | Project ID: %s",
            project_id
        )

        return {
            "status": "success",
            "project_id": str(project_id),
            "final_video": project.final_video.name,
        }

    except Exception:
        logger.exception(
            "Final video assembly failed | Project ID: %s",
            project_id
        )

        try:
            project = Project.objects.get(pk=project_id)
            project.status = "failed"
            project.error_message = "Video assembly failed. Check application logs."
            project.save()
        except Exception:
            logger.exception(
                "Could not update project failure status | Project ID: %s",
                project_id
            )

        raise
