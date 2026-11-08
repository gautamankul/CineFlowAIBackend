"""Celery tasks for CineFlowAI. Run GPU tasks with --pool=solo --concurrency=1."""
import logging

from celery import shared_task
from .cuda_ai.text_model import make_storyboard
from .cuda_ai.image_model import generate_image, unload_image_pipeline
from .cuda_ai.video_model import generate_clip, unload_wan
from .ai.editor import assemble
from .models import Project, Scene

logger = logging.getLogger(__name__)


@shared_task
def generate_storyboard_task(project_id, scene_count):
    logger.info("Starting storyboard generation | Project ID: %s", project_id)
    try:
        project = Project.objects.get(pk=project_id)
        # Generate first; don't delete existing scenes if model generation fails.
        storyboard = make_storyboard(project.prompt, project.style, scene_count)
        project.scenes.all().delete()
        for index, scene_data in enumerate(storyboard, start=1):
            Scene.objects.create(project=project, scene_number=index, **scene_data)
        project.status = "storyboard_generated"
        project.error_message = ""
        project.save(update_fields=["status", "error_message"])
        logger.info("Storyboard created | Project ID: %s | Scenes: %s", project_id, len(storyboard))
        return {"status": "success", "project_id": str(project_id), "scenes_created": len(storyboard)}
    except Exception:
        logger.exception("Storyboard generation failed | Project ID: %s", project_id)
        try:
            Project.objects.filter(pk=project_id).update(
                status="failed", error_message="Storyboard generation failed. Check Celery logs."
            )
        except Exception:
            logger.exception("Could not record project failure | Project ID: %s", project_id)
        raise


@shared_task
def generate_scene_task(scene_id):
    logger.info("Starting scene generation | Scene ID: %s", scene_id)
    try:
        scene = Scene.objects.get(pk=scene_id)
        scene.status = "generating_image"
        scene.error_message = ""
        scene.save(update_fields=["status", "error_message"])

        # Stage 1: save image path to database before attempting video.
        try:
            image_path = generate_image(scene, release_gpu=True)
            scene.reference_image.name = image_path
            scene.save(update_fields=["reference_image"])
            logger.info("Image completed | Scene ID: %s", scene_id)
        finally:
            unload_image_pipeline()

        # Stage 2: Wan loading only starts after image model is unloaded.
        scene.status = "generating_video"
        scene.save(update_fields=["status"])
        try:
            video_path = generate_clip(scene, release_gpu=True)
            scene.video.name = video_path
            scene.save(update_fields=["video"])
            logger.info("Video completed | Scene ID: %s", scene_id)
        finally:
            unload_wan()

        scene.status = "completed"
        scene.save(update_fields=["status"])
        logger.info("Scene completed | Scene ID: %s", scene_id)
        return {"status": "success", "scene_id": scene_id}
    except Exception:
        logger.exception("Scene generation failed | Scene ID: %s", scene_id)
        try:
            Scene.objects.filter(pk=scene_id).update(
                status="failed",
                error_message="Scene generation failed. Check Celery logs for details.",
            )
        except Exception:
            logger.exception("Could not record scene failure | Scene ID: %s", scene_id)
        raise


@shared_task
def assemble_video_task(project_id):
    logger.info("Starting video assembly | Project ID: %s", project_id)
    try:
        project = Project.objects.get(pk=project_id)
        project.final_video.name = assemble(project)
        project.status = "completed"
        project.error_message = ""
        project.save(update_fields=["final_video", "status", "error_message"])
        return {
            "status": "success",
            "project_id": str(project_id),
            "final_video": project.final_video.name,
        }
    except Exception:
        logger.exception("Video assembly failed | Project ID: %s", project_id)
        try:
            Project.objects.filter(pk=project_id).update(
                status="failed", error_message="Video assembly failed. Check Celery logs."
            )
        except Exception:
            logger.exception("Could not record assembly failure | Project ID: %s", project_id)
        raise
