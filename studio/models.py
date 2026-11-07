
import uuid

from django.db import models


class Project(models.Model):
    STATUS = [
        ("draft", "Draft"),
        ("storyboard_generated", "Storyboard Generated"),
        ("generating", "Generating"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=120)
    prompt = models.TextField()
    style = models.CharField(
        max_length=50,
        default="Cinematic realism",
    )
    aspect_ratio = models.CharField(
        max_length=10,
        default="16:9",
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS,
        default="draft",
    )
    final_video = models.FileField(
        upload_to="final/",
        null=True,
        blank=True,
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Character(models.Model):
    project = models.ForeignKey(
        Project,
        related_name="characters",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=80)
    appearance = models.TextField(blank=True)
    clothing = models.TextField(blank=True)
    reference_image = models.ImageField(
        upload_to="characters/",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Scene(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("generating_image", "Generating Image"),
        ("image_ready", "Image Ready"),
        ("generating_video", "Generating Video"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    project = models.ForeignKey(
        Project,
        related_name="scenes",
        on_delete=models.CASCADE,
    )
    scene_number = models.PositiveIntegerField()
    title = models.CharField(
        max_length=120,
        default="Untitled Scene",
    )
    description = models.TextField(blank=True)
    characters = models.ManyToManyField(
        Character,
        blank=True,
    )
    camera_movement = models.CharField(
        max_length=120,
        blank=True,
    )
    lighting = models.CharField(
        max_length=120,
        blank=True,
    )
    image_prompt = models.TextField(blank=True)
    video_prompt = models.TextField(blank=True)
    reference_image = models.ImageField(
        upload_to="scenes/images/",
        null=True,
        blank=True,
    )
    video = models.FileField(
        upload_to="scenes/videos/",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS,
        default="pending",
    )
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["scene_number"]

    def __str__(self):
        return f"{self.project.name} - Scene {self.scene_number}"
