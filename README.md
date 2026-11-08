# 🎬 CineFlowAI – AI-Powered Short Film & Video Generator

CineFlowAI is an AI-powered video production studio that transforms text prompts into cinematic short films. It uses AI models to generate storyboards, scene images, video clips, and complete videos.

Users can create science-fiction films, historical documentaries, educational videos, and other cinematic content.

---

## ✨ Features

- **AI Storyboard Generation:** Convert text prompts into structured cinematic scenes.
- **AI Image Generation:** Generate scene images using Stable Diffusion 1.5.
- **AI Video Generation:** Turn scene prompts into video clips using Wan 2.1.
- **AI Text Generation:** Generate stories and scene descriptions using Qwen 2.5.
- **Video Assembly:** Combine generated scene clips into a final video.
- **Scene Management:** Regenerate individual scenes.
- **Celery Background Tasks:** Run AI generation asynchronously.
- **Task Logging:** Record successful tasks and errors.
- **Project Management:** Create, view, and manage multiple video projects.
- **Multiple Aspect Ratios:** Support cinematic and vertical video formats.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | React |
| Backend | Python, Django |
| API | Django REST Framework |
| Background Tasks | Celery |
| Message Broker | Redis (if configured) |
| Text Generation | Qwen 2.5 1.5B Instruct |
| Image Generation | Stable Diffusion 1.5 |
| Video Generation | Wan 2.1 T2V 1.3B |
| Deep Learning | PyTorch |
| AI Framework | Hugging Face Transformers and Diffusers |
| Video Processing | FFmpeg |
| Storage | Django Media Storage |

---

# 🚀 Getting Started

## 1. Prerequisites

Install the following software:

- Python 3.10 or newer
- Node.js and npm
- Redis
- Git
- FFmpeg
- Hugging Face account
- NVIDIA GPU recommended for AI generation

Check installations:

```bash
python --version
node --version
npm --version
redis-server --version
ffmpeg -version
```

**Hardware note:** Running all three AI models locally requires substantial RAM and GPU memory. CPU fallback may work for some operations but can be very slow. Check model compatibility and hardware requirements before generating videos.

## 2. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
```

Navigate to the project:

```bash
cd CineFlowAI
```

Expected project structure:

```text
CineFlowAI/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   │
│   ├── studio/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── tasks.py
│   │   │
│   │   └── ai/
│   │       ├── text_model.py
│   │       ├── image_model.py
│   │       ├── video_model.py
│   │       └── editor.py
│   │
│   └── media/
│
└── frontend/
    ├── package.json
    ├── src/
    └── public/
```

*The structure above illustrates the expected organization; adjust paths to match your repository.*

---

# ⚙️ Backend Setup

## 3. Create a Python Virtual Environment

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

## 4. Install Python Dependencies

```bash
pip install --upgrade pip
```

Install project requirements:

```bash
pip install -r requirements.txt
```

If you haven't created `requirements.txt`, install the core dependencies:

```bash
pip install django djangorestframework
pip install celery redis
pip install python-dotenv
pip install torch torchvision
pip install transformers accelerate
pip install diffusers
pip install imageio imageio-ffmpeg
pip install pillow
```

Install a PyTorch build compatible with your NVIDIA CUDA environment by following the official instructions:

https://pytorch.org/get-started/locally/

## 5. Configure Environment Variables

Create a `.env` file inside the backend directory.

```env
# Django
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Hugging Face
HF_TOKEN=hf_your_actual_token

# Celery
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1

# Hugging Face configuration
HF_HUB_DISABLE_TELEMETRY=1
HF_HUB_DISABLE_PROGRESS_BARS=1
TOKENIZERS_PARALLELISM=false
TRANSFORMERS_VERBOSITY=error

# Python warnings
PYTHONWARNINGS=ignore::FutureWarning
```

Get your Hugging Face token:

https://huggingface.co/settings/tokens

Never commit your `.env` file to GitHub.

Add this to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
media/
logs/
```

## 6. Database Migration

Run:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create an administrator account:

```bash
python manage.py createsuperuser
```

## 7. Start the Django Backend with redis and celery broker

```bash
python manage.py runserver 127.0.0.1:8000        terminal 1
celery -A cineflow worker --loglevel=info        terminal 2 
celery -A cineflow worker -l info --pool=solo    for window only 
celery -A cineflow worker --concurrency=1         for speesd up
redis-server                                     terminal 3

```

Backend URL:

http://127.0.0.1:8000/

---

# 🔄 Celery Background Worker

CineFlowAI uses Celery to execute AI generation tasks in the background.

## 8. Start Redis

Start your Redis server.

```bash
redis-server
```

Verify Redis:

```bash
redis-cli ping
```

Expected response:

```text
PONG
```

## 9. Start Celery Worker

Open another terminal.

Navigate to the backend directory and activate the virtual environment.

Run:

```bash
celery -A YOUR_DJANGO_PROJECT worker --loglevel=info
```

Replace `YOUR_DJANGO_PROJECT` with the Django project module containing your Celery application.

For GPU-intensive video generation, use a dedicated worker with concurrency set to one:

```bash
celery -A YOUR_DJANGO_PROJECT worker \
    --loglevel=info \
    --concurrency=1
```

If you have configured separate Celery queues, start workers for the corresponding queues.

---

# 🎨 Frontend Setup

## 10. Install Frontend Dependencies

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

## 11. Configure Frontend API

Ensure your frontend API configuration points to your Django backend.

For example:

```javascript
const API_BASE_URL = "http://127.0.0.1:8000";
```

Your API service should use the correct backend endpoints and authentication configuration.

## 12. Start React Development Server

```bash
npm run dev
```

If your project uses Create React App instead of Vite:

```bash
npm start
```

Open the frontend URL displayed in your terminal.

---

# 🎥 How to Create an AI Film

## 13. Create Your First Project

Open CineFlowAI and create a new project.

Enter:

| Field | Example |
|---|---|
| Project Title | My First AI Film |
| Genre | Science Fiction |
| Style | Cinematic Realism |
| Aspect Ratio | 16:9 |
| Scene Count | 3 |
| Duration | 60 Seconds |

## 14. Provide Your Film Prompt

Example:

**Title: The Awakening**

```text
Create a cinematic science-fiction film set
in Neo Aurora, a futuristic city in 2085.

Scientist Arin stands on a rooftop at sunset.
A mysterious blue energy pulse appears above
the skyscrapers.

The city features enormous futuristic buildings,
glowing neon lights, flying vehicles, and
advanced technology.

Use cinematic camera movements, realistic
lighting, atmospheric fog, and dramatic
science-fiction visuals.

Maintain consistent character appearance
throughout all scenes.
```

## 15. Generate the Storyboard

Click **Generate Storyboard**.

The Qwen model generates:

- Scene title
- Scene description
- Camera movement
- Lighting
- Image prompt
- Video prompt

The generated scenes are saved in the database.

## 16. Generate Scene Images and Videos

Click **Generate All Clips**.

The background workers execute the following operations:

1. Generate scene images using Stable Diffusion.
2. Save generated images in the media directory.
3. Generate video clips using Wan 2.1.
4. Save generated video files.
5. Update scene generation status.

You can also regenerate individual scenes.

## 17. Assemble Final Video

When all scenes have completed successfully, click:

**Assemble Final Video**

The video editor combines the generated clips into one final film.

The completed video is saved in Django media storage and displayed in the project page.

---

# 🤖 AI Models

| Model | Purpose |
|---|---|
| Qwen/Qwen2.5-1.5B-Instruct | Storyboard and text generation |
| stable-diffusion-v1-5/stable-diffusion-v1-5 | Scene image generation |
| Wan-AI/Wan2.1-T2V-1.3B-Diffusers | Text-to-video generation |

Models are downloaded from Hugging Face when first loaded, subject to availability and access permissions.

---

# 📁 Generated Media

Generated files are stored under Django's media directory.

```text
backend/
│
└── media/
    └── scenes/
        ├── images/
        │   ├── scene_1.png
        │   └── scene_2.png
        │
        └── videos/
            ├── scene_1.mp4
            └── scene_2.mp4
```

The actual filenames are generated dynamically.

Make sure your Django media configuration is correct:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

For local development, configure media serving in your Django URL configuration.

---

# 📊 Example Projects

## Project 1: My First AI Film

**Genre:** Science Fiction

**Style:** Cinematic Realism

**Duration:** 60 Seconds

**Aspect Ratio:** 16:9

### Scene 1 – The Mysterious Signal

Neo Aurora, a futuristic city in 2085. Scientist Arin stands on a rooftop at sunset. A mysterious blue energy pulse appears above the skyscrapers.

### Scene 2 – The Secret Discovery

Arin investigates the signal inside a futuristic laboratory. Holographic displays reveal an ancient structure beneath the city.

### Scene 3 – The Final Awakening

Arin discovers a giant floating crystal in an underground chamber. The crystal activates a cosmic gateway and sends a beam of light into the sky.

**Ending Title:** THE AWAKENING

---

## Project 2: Dalit History

**Genre:** Historical Documentary

**Style:** Cinematic Realism

**Duration:** 60 Seconds

**Language:** Hindi

**Aspect Ratio:** 16:9

### Scene 1 – The Struggle for Dignity

Show Dalit communities facing caste-based discrimination in early twentieth-century India, including restrictions on public water access and education.

**Hindi Voiceover:**

भारत के इतिहास में दलित समाज ने सदियों तक जातिगत भेदभाव और अन्याय का सामना किया। लेकिन समानता और सम्मान के लिए उनका संघर्ष कभी रुका नहीं।

### Scene 2 – Dr. B. R. Ambedkar and the Movement

Show Dr. B. R. Ambedkar studying, addressing gatherings, and leading the Mahad Satyagraha of 1927.

**Hindi Voiceover:**

डॉ. भीमराव आंबेडकर ने शिक्षा, संगठन और संघर्ष को सामाजिक बदलाव का आधार बनाया। 1927 का महाड़ सत्याग्रह समान अधिकारों की लड़ाई में एक ऐतिहासिक कदम बना।

### Scene 3 – Constitution, Equality and Legacy

Show the Constitution of India, Ambedkar's contribution to constitution-making, and contemporary achievements in education, science, law, and arts.

**Hindi Voiceover:**

भारत के संविधान ने समानता और अस्पृश्यता के उन्मूलन को कानूनी आधार दिया। आज भी दलित समाज शिक्षा, अधिकार और सम्मान के लिए आगे बढ़ रहा है। यह इतिहास संघर्ष, साहस और बदलाव का इतिहास है।

**Ending Title:**

EDUCATION • EQUALITY • DIGNITY • JUSTICE

---

# 🐛 Troubleshooting

### 1. Hugging Face Authentication Error

Check your `.env` file:

```env
HF_TOKEN=hf_your_actual_token
```

Restart Django and Celery after changing environment variables.

### 2. CUDA Out of Memory

Try:

- Reducing image resolution.
- Reducing video frame count.
- Running only one GPU-intensive task at a time.
- Enabling model CPU offloading for Wan.
- Using separate Celery workers for different models.

### 3. Redis Connection Error

Make sure Redis is running:

```bash
redis-cli ping
```

Check your Celery broker URL:

```env
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
```

### 4. Video Generation Error

Check:

- Hugging Face model availability.
- PyTorch and Diffusers compatibility.
- Available GPU memory.
- Celery worker logs.
- FFmpeg installation.

### 5. Project Not Found

Check:

- Django backend is running.
- Project ID is correct.
- API endpoint returns HTTP 200.
- Frontend correctly parses the Fetch API response using `await response.json()`.

### 6. Check Application Logs

Inspect the configured log file:

```text
backend/logs/celery_tasks.log
```

Also check the Celery worker terminal for task failures and traceback details.

---

# 🔐 Security

- Never expose Hugging Face tokens in frontend code.
- Keep `.env` out of Git.
- Use a secure Django `SECRET_KEY`.
- Set `DEBUG=False` in production.
- Configure `ALLOWED_HOSTS`.
- Protect project and media endpoints with appropriate permissions.
- Use a production-grade media storage solution when deploying.

---

# 🚀 Production Deployment

For production, configure:

- Django with Gunicorn or another production WSGI/ASGI server.
- React production build.
- Redis as the Celery message broker.
- Dedicated Celery GPU workers.
- Nginx or another reverse proxy.
- Persistent database and media storage.
- Rotating application logs.
- Environment-based configuration.

Do not expose Django's development server or Redis directly to the public internet.

---

# 📌 Project Summary

| Metric | Value |
|---|---|
| Project Name | CineFlowAI |
| Application Type | AI Video Production Studio |
| Frontend | React |
| Backend | Django |
| Background Processing | Celery |
| Text AI | Qwen 2.5 |
| Image AI | Stable Diffusion 1.5 |
| Video AI | Wan 2.1 |
| Video Assembly | FFmpeg-based editor |
| Output | Short Cinematic Videos |
| Supported Formats | Vertical and Landscape |

---

**CineFlowAI – From Imagination to Cinema.**

Transform your ideas into stories, scenes, and cinematic videos using AI.