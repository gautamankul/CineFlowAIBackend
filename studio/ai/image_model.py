# pip install diffusers
import torch, uuid, os
from django.conf import settings
from diffusers import StableDiffusionPipeline

_pipe = None


def generate_image(scene):
    global _pipe
    if _pipe is None:
        _pipe = StableDiffusionPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5",
                                                        torch_dtype=torch.float16).to("cuda")
    img = _pipe(scene.image_prompt, num_inference_steps=25).images[0]
    rel = f"scenes/images/{uuid.uuid4().hex}.png"
    path = os.path.join(settings.MEDIA_ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return rel
