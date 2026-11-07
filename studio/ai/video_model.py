
import os
import uuid
import logging
import warnings
from dotenv import load_dotenv
import torch
from django.conf import settings
from diffusers import AutoencoderKLWan, WanPipeline
from diffusers.utils import export_to_video
from transformers import logging as transformers_logging

# Load environment variables first
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

# Hugging Face configuration
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

warnings.filterwarnings("ignore", category=FutureWarning)

transformers_logging.set_verbosity_error()

logger = logging.getLogger(__name__)

MODEL_ID = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"

_pipe = None


def load_video_model():
    global _pipe

    if _pipe is not None:
        return _pipe

    logger.info("Loading Wan video generation model...")

    try:
        dtype = (
            torch.bfloat16
            if torch.cuda.is_available()
            and torch.cuda.is_bf16_supported()
            else torch.float16
        )

        vae = AutoencoderKLWan.from_pretrained(
            MODEL_ID,
            subfolder="vae",
            torch_dtype=torch.float32,
            token=HF_TOKEN,
        )

        _pipe = WanPipeline.from_pretrained(
            MODEL_ID,
            vae=vae,
            torch_dtype=dtype,
            token=HF_TOKEN,
        )

        # Efficient GPU memory management
        _pipe.enable_model_cpu_offload()

        logger.info("Wan video model loaded successfully")

        return _pipe

    except Exception:
        logger.exception("Failed to load Wan video model")
        _pipe = None
        raise


def generate_clip(scene):
    logger.info(
        "Starting video generation | Scene ID: %s",
        scene.id,
    )

    try:
        pipe = load_video_model()

        prompt = scene.video_prompt

        result = pipe(
            prompt=prompt,
            height=480,
            width=832,
            num_frames=33,
            guidance_scale=5.0,
        )

        frames = result.frames[0]

        rel = f"scenes/videos/{uuid.uuid4().hex}.mp4"

        path = os.path.join(
            settings.MEDIA_ROOT,
            rel,
        )

        os.makedirs(
            os.path.dirname(path),
            exist_ok=True,
        )

        export_to_video(
            frames,
            path,
            fps=16,
        )

        logger.info(
            "Video generated successfully | Scene ID: %s | File: %s",
            scene.id,
            rel,
        )

        return rel

    except Exception:
        logger.exception(
            "Video generation failed | Scene ID: %s",
            scene.id,
        )

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        raise
