
import os
import uuid
import logging
import warnings

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

# Hugging Face configuration
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

warnings.filterwarnings("ignore", category=FutureWarning)

import torch

from django.conf import settings
from diffusers import StableDiffusionPipeline
from transformers import logging as transformers_logging

transformers_logging.set_verbosity_error()

logger = logging.getLogger(__name__)

MODEL_ID = "stable-diffusion-v1-5/stable-diffusion-v1-5"

_pipe = None


def load_image_model():
    global _pipe

    if _pipe is not None:
        return _pipe

    logger.info("Loading Stable Diffusion image model...")

    try:
        if torch.cuda.is_available():
            device = "cuda"

            dtype = (
                torch.float16
                if torch.cuda.is_available()
                else torch.float32
            )
        else:
            device = "cpu"
            dtype = torch.float32

        _pipe = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=dtype,
            token=HF_TOKEN,
            safety_checker=None,
        )

        _pipe = _pipe.to(device)

        # Reduce memory usage
        _pipe.enable_attention_slicing()

        logger.info(
            "Stable Diffusion loaded successfully | Device: %s",
            device,
        )

        return _pipe

    except Exception:
        logger.exception("Failed to load Stable Diffusion model")
        _pipe = None
        raise


def generate_image(scene):
    logger.info(
        "Starting image generation | Scene ID: %s",
        scene.id,
    )

    try:
        pipe = load_image_model()

        image = pipe(
            prompt=scene.image_prompt,
            num_inference_steps=25,
            guidance_scale=7.5,
            height=512,
            width=512,
        ).images[0]

        rel = f"scenes/images/{uuid.uuid4().hex}.png"

        path = os.path.join(
            settings.MEDIA_ROOT,
            rel,
        )

        os.makedirs(
            os.path.dirname(path),
            exist_ok=True,
        )

        image.save(path)

        logger.info(
            "Image generated successfully | Scene ID: %s | File: %s",
            scene.id,
            rel,
        )

        return rel

    except Exception:
        logger.exception(
            "Image generation failed | Scene ID: %s",
            scene.id,
        )

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        raise
