
import os
import json
import logging
import warnings

from dotenv import load_dotenv

# Load .env BEFORE importing Hugging Face libraries
load_dotenv()

# Environment configuration
HF_TOKEN = os.getenv("HF_TOKEN")

os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Suppress unnecessary Python warnings
# Prefer filtering specific warnings over hiding all warnings.
warnings.filterwarnings("ignore", category=FutureWarning)

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    logging as transformers_logging,
)

# Disable Transformers informational and warning logs
transformers_logging.set_verbosity_error()

logger = logging.getLogger(__name__)

_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

_tok = None
_model = None


def make_storyboard(prompt, style, n):
    global _tok, _model

    try:
        if _model is None:
            logger.info("Loading Hugging Face model: %s", _NAME)

            _tok = AutoTokenizer.from_pretrained(
                _NAME,
                token=HF_TOKEN,
            )

            _model = AutoModelForCausalLM.from_pretrained(
                _NAME,
                torch_dtype="auto",
                device_map="auto",
                token=HF_TOKEN,
            )

            logger.info("Hugging Face model loaded successfully")

        msgs = [
            {
                "role": "system",
                "content": (
                    "Return ONLY a valid JSON list. "
                    "Each item must contain these keys: "
                    "title, description, camera_movement, "
                    "lighting, image_prompt, video_prompt."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Style: {style}. "
                    f"Create {n} scenes for: {prompt}"
                ),
            },
        ]

        text = _tok.apply_chat_template(
            msgs,
            tokenize=False,
            add_generation_prompt=True,
        )

        ids = _tok(
            text,
            return_tensors="pt",
        ).to(_model.device)

        with torch.inference_mode():
            out = _model.generate(
                **ids,
                max_new_tokens=1500,
                do_sample=True,
                temperature=0.7,
                pad_token_id=_tok.eos_token_id,
            )

        raw = _tok.decode(
            out[0][ids.input_ids.shape[1]:],
            skip_special_tokens=True,
        )

        # Extract JSON
        start = raw.find("[")
        end = raw.rfind("]")

        if start == -1 or end == -1:
            raise ValueError("Model did not return valid JSON.")

        result = json.loads(raw[start:end + 1])

        if not isinstance(result, list):
            raise ValueError("Storyboard response must be a JSON list.")

        logger.info(
            "Storyboard generated successfully: %s scenes",
            len(result[:n]),
        )

        return result[:n]

    except Exception:
        logger.exception("Storyboard generation failed")
        raise
