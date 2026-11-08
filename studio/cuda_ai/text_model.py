
import json
import re
import gc
import threading

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
DEVICE = torch.device("cuda:0")

_tok = None
_model = None
_model_lock = threading.RLock()


def check_cuda():
    if torch.version.cuda is None:
        raise RuntimeError(
            "CPU-only PyTorch detected. Install the "
            "CUDA-enabled PyTorch build in your Django "
            "and Celery virtual environment."
        )

    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is unavailable. Check your NVIDIA "
            "driver and WSL2 GPU configuration."
        )

    print("CUDA version:", torch.version.cuda)
    print("GPU:", torch.cuda.get_device_name(0))


def load_storyboard_model():
    global _tok, _model

    with _model_lock:
        if _model is not None:
            return

        check_cuda()

        print("Loading Qwen model on GPU...")

        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            attn_implementation="sdpa",
        )

        model = model.to(DEVICE)
        model.eval()

        _tok = tokenizer
        _model = model

        print("Qwen loaded on:", next(model.parameters()).device)


def unload_storyboard_model():
    global _tok, _model

    with _model_lock:
        _model = None
        _tok = None

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        print("Storyboard model unloaded")


def extract_json(raw):
    raw = re.sub(
        r"```(?:json)?",
        "",
        raw
    ).strip()

    start = raw.find("[")

    if start == -1:
        raise ValueError(
            "No JSON array found in model response"
        )

    decoder = json.JSONDecoder()

    result, _ = decoder.raw_decode(
        raw[start:]
    )

    if not isinstance(result, list):
        raise ValueError("Expected JSON list")

    return result


def make_storyboard(
    prompt,
    style="cinematic",
    n=4,
    release_gpu=True,
):
    if not 1 <= n <= 10:
        raise ValueError(
            "Scene count must be between 1 and 10"
        )

    with _model_lock:
        try:
            load_storyboard_model()

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a professional film "
                        "director and storyboard artist. "
                        "Return ONLY a valid JSON array. "
                        "No markdown or explanations. "
                        "Every scene must contain: "
                        "title, description, "
                        "camera_movement, lighting, "
                        "image_prompt, video_prompt. "
                        "Make scenes visually consistent "
                        "and sequential."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Style: {style}\n"
                        f"Create exactly {n} scenes "
                        f"for this story:\n{prompt}"
                    ),
                },
            ]

            text = _tok.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

            inputs = _tok(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=4096,
            ).to(DEVICE)

            max_tokens = min(
                1500,
                250 + n * 300
            )

            with torch.inference_mode():
                output = _model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    use_cache=True,
                    pad_token_id=_tok.eos_token_id,
                )

            generated = output[
                0,
                inputs.input_ids.shape[1]:
            ]

            raw = _tok.decode(
                generated,
                skip_special_tokens=True,
            )

            scenes = extract_json(raw)

            if len(scenes) != n:
                raise ValueError(
                    f"Expected {n} scenes, "
                    f"received {len(scenes)}"
                )

            return scenes

        finally:
            # Drop local GPU tensor references before
            # releasing the model and CUDA cache.
            if "generated" in locals():
                del generated

            if "output" in locals():
                del output

            if "inputs" in locals():
                del inputs

            if release_gpu:
                unload_storyboard_model()
