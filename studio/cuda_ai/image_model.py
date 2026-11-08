"""Stable Diffusion 1.5 + LCM LoRA, serialized for a single GPU worker."""
import gc
import logging
import threading
import uuid
from pathlib import Path

import torch
from django.conf import settings
from diffusers import LCMScheduler, StableDiffusionPipeline

logger = logging.getLogger(__name__)
MODEL_ID = "stable-diffusion-v1-5/stable-diffusion-v1-5"
LORA_ID = "latent-consistency/lcm-lora-sdv1-5"
_pipe = None
_pipe_lock = threading.RLock()


def cleanup_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def get_pipeline():
    global _pipe
    with _pipe_lock:
        if _pipe is not None:
            return _pipe
        if not torch.cuda.is_available():
            raise RuntimeError(f"CUDA unavailable (torch={torch.__version__}, build={torch.version.cuda})")

        pipe = None
        try:
            logger.info("Loading Stable Diffusion on %s", torch.cuda.get_device_name(0))
            pipe = StableDiffusionPipeline.from_pretrained(
                MODEL_ID, torch_dtype=torch.float16, use_safetensors=True
            )
            pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
            pipe.load_lora_weights(LORA_ID)
            pipe.fuse_lora()
            pipe.unload_lora_weights()
            # Do not enable attention slicing when using SDPA/xFormers: it can slow inference.
            pipe.to("cuda:0")
            pipe.set_progress_bar_config(disable=True)
            _pipe = pipe
            return _pipe
        except BaseException:
            pipe = None
            cleanup_memory()
            raise


def unload_image_pipeline():
    global _pipe
    with _pipe_lock:
        _pipe = None
        cleanup_memory()
        logger.info("Stable Diffusion pipeline released")


def generate_image(scene, release_gpu=True):
    """Return a path relative to MEDIA_ROOT; do not save the Django model here."""
    global _pipe
    with _pipe_lock:
        prompt = (scene.image_prompt or "").strip()
        if not prompt:
            raise ValueError("Scene image_prompt is empty")
        pipe = result = image = None
        try:
            pipe = get_pipeline()
            with torch.inference_mode():
                result = pipe(
                    prompt=prompt,
                    num_inference_steps=4,
                    guidance_scale=0.0,
                    width=512,
                    height=512,
                )
            image = result.images[0]
            rel_path = f"scenes/images/{uuid.uuid4().hex}.png"
            full_path = Path(settings.MEDIA_ROOT) / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(full_path)
            logger.info("Saved image for scene %s: %s", scene.pk, rel_path)
            return rel_path
        finally:
            image = None
            result = None
            if release_gpu:
                _pipe = None
                pipe = None
            cleanup_memory()
