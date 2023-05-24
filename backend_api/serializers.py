from rest_framework import serializers
from .models import User, Project, Image, Judgement

class JudgementSerializer(serializers.ModelSerializer):
  class Meta:
    model = Judgement
    fields = ['first', 'second', 'first_duration', 'second_duration']

class ImageSerializer(serializers.ModelSerializer):
  judgement = JudgementSerializer(many=True, read_only=True)
  class Meta:
    model = Image
    fields = ['tissue', 'resolution', 'judgement']

class ProjectSerializer(serializers.ModelSerializer):
  images = ImageSerializer(many=True, read_only=True)
  class Meta:
    model = Project
    fields = ['p_id', 'title', 'type', 'path', 'images']

class UserSerializer(serializers.ModelSerializer):
  projects = ProjectSerializer(many=True, read_only=True)
  class Meta:
    model = User
    fields = ['u_id', 'name', 'mail', 'password', 'projects']
