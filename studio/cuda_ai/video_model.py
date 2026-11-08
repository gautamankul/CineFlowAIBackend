"""Wan2.1 T2V inference with conservative GPU usage.

Note: sequential CPU offload saves VRAM, not system RAM. The unquantized
Wan text encoder may still exceed a 16-GB Windows machine's memory budget.
"""
import gc
import logging
import threading
import time
import uuid
import torch
from django.conf import settings
from pathlib import Path
from diffusers import AutoencoderKLWan, WanPipeline
from diffusers.schedulers.scheduling_unipc_multistep import UniPCMultistepScheduler
from diffusers.utils import export_to_video
from django.utils.text import slugify

logger = logging.getLogger(__name__)
MODEL_ID = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
_pipe = None
_pipe_lock = threading.RLock()

# Smoke-test settings; 9 frames at 16 FPS = 0.56 seconds.
WIDTH = 448
HEIGHT = 256
NUM_FRAMES = 9
NUM_STEPS = 12
FPS = 16


def cleanup_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def check_cuda():
    if not torch.cuda.is_available():
        raise RuntimeError(f"CUDA unavailable (torch={torch.__version__}, build={torch.version.cuda})")
    logger.info("GPU: %s | CUDA build: %s", torch.cuda.get_device_name(0), torch.version.cuda)


def load_wan():
    global _pipe
    with _pipe_lock:
        if _pipe is not None:
            return _pipe
        check_cuda()
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        vae = pipe = None
        try:
            logger.info("Wan load step 1/3: VAE")
            vae = AutoencoderKLWan.from_pretrained(
                MODEL_ID, subfolder="vae", torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
            )
            logger.info("Wan load step 2/3: pipeline components (CPU RAM intensive)")
            pipe = WanPipeline.from_pretrained(
                MODEL_ID, vae=vae, torch_dtype=dtype,
                low_cpu_mem_usage=True,
            )
            pipe.scheduler = UniPCMultistepScheduler.from_config(
                pipe.scheduler.config, flow_shift=3.0
            )
            logger.info("Wan load step 3/3: sequential CPU offload")
            pipe.enable_sequential_cpu_offload(device="cuda:0")
            if hasattr(pipe.vae, "enable_tiling"):
                pipe.vae.enable_tiling()
            pipe.set_progress_bar_config(disable=False)
            _pipe = pipe
            logger.info("Wan pipeline ready")
            return _pipe
        except BaseException:
            _pipe = None
            pipe = None
            vae = None
            cleanup_memory()
            raise


def unload_wan():
    global _pipe
    with _pipe_lock:
        _pipe = None
        cleanup_memory()
        logger.info("Wan pipeline reference cleared")


def generate_clip_old(scene, release_gpu=True):
    global _pipe
    with _pipe_lock:
        prompt = (scene.video_prompt or "").strip()
        if not prompt:
            raise ValueError("Scene video_prompt is empty")
        pipe = result = frames = None


def generate_clip(scene, release_gpu=True):
    """Generate a video and save it under the project title."""
    global _pipe

    with _pipe_lock:
        prompt = (scene.video_prompt or "").strip()

        if not prompt:
            raise ValueError("Scene video_prompt is empty")

        # Get project title.
        project_title = scene.project.name

        # Convert title into a safe folder name.
        title = (
                slugify(project_title)
                or f"project-{scene.project_id}"
        )

        start_time = time.time()

        pipe = None
        result = None
        frames = None

        try:
            check_cuda()

            pipe = load_wan()

            cleanup_memory()

            torch.cuda.reset_peak_memory_stats()

            logger.info(
                "Generating video | Scene ID: %s",
                scene.pk,
            )

            with torch.inference_mode():
                result = pipe(
                    prompt=prompt,
                    height=HEIGHT,
                    width=WIDTH,
                    num_frames=NUM_FRAMES,
                    num_inference_steps=NUM_STEPS,
                    guidance_scale=5.0,
                )

            frames = result.frames[0]

            torch.cuda.synchronize()

            elapsed = time.time() - start_time

            peak_vram = (
                    torch.cuda.max_memory_allocated()
                    / (1024 ** 3)
            )

            logger.info(
                "Video generation time: %.1f seconds",
                elapsed,
            )

            logger.info(
                "Peak GPU memory: %.2f GiB",
                peak_vram,
            )

            # Save under: title/scenes/videos/uuid.mp4
            rel_path = (
                f"{title}/scenes/videos/"
                f"{uuid.uuid4().hex}.mp4"
            )

            full_path = (
                    Path(settings.MEDIA_ROOT) / rel_path
            )

            full_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            export_to_video(
                frames,
                str(full_path),
                fps=FPS,
            )

            logger.info(
                "Video saved | Scene ID: %s | Path: %s",
                scene.pk,
                rel_path,
            )

            return rel_path

        except Exception:
            logger.exception(
                "Video generation failed | Scene ID: %s",
                scene.pk,
            )
            raise

        finally:
            frames = None
            result = None

            if release_gpu:
                _pipe = None
                pipe = None

            cleanup_memory()
