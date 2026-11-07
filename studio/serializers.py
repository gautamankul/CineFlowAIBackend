from rest_framework import serializers
from .models import Project, Scene, Character

class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = "__all__"

class SceneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scene
        fields = "__all__"

class ProjectSerializer(serializers.ModelSerializer):
    scenes = SceneSerializer(many=True, read_only=True)
    characters = CharacterSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"