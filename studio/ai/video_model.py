import torch, uuid, os
from django.conf import settings
from diffusers import AutoencoderKLWan, WanPipeline
from diffusers.utils import export_to_video

_pipe = None

def generate_clip(scene):
    global _pipe
    if _pipe is None:
        mid = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
        vae = AutoencoderKLWan.from_pretrained(mid, subfolder="vae", torch_dtype=torch.float32)
        _pipe = WanPipeline.from_pretrained(mid, vae=vae, torch_dtype=torch.bfloat16)
        _pipe.enable_model_cpu_offload()
    frames = _pipe(prompt=scene.video_prompt, height=480, width=832,
                   num_frames=33, guidance_scale=5.0).frames[0]
    rel = f"scenes/videos/{uuid.uuid4().hex}.mp4"
    path = os.path.join(settings.MEDIA_ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    export_to_video(frames, path, fps=16)
    return rel