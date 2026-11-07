import subprocess, os, uuid
from django.conf import settings

def assemble(project):
    clips = [s.video.path for s in project.scenes.all() if s.video]
    listfile = os.path.join(settings.MEDIA_ROOT, f"{uuid.uuid4().hex}.txt")
    with open(listfile, "w") as f:
        for c in clips:
            f.write(f"file '{c}'\n")
    rel = f"final/{project.id}.mp4"
    out = os.path.join(settings.MEDIA_ROOT, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile,
                    "-c", "copy", out], check=True)
    os.remove(listfile)
    return rel