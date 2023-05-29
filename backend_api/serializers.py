from rest_framework import serializers
from .models import User, Project, Image, Judgement

class JudgementSerializer(serializers.ModelSerializer):
  class Meta:
    model = Judgement
    fields = ['j_id', 'firstJudge', 'secondJudge', 'firstDuration', 'secondDuration', 'created_time']

class ImageSerializer(serializers.ModelSerializer):
  judgement = JudgementSerializer(many=True)
  class Meta:
    model = Image
    fields = ['i_id', 'name', 'path', 'judgements']

class ProjectSerializer(serializers.ModelSerializer):
  images = ImageSerializer(many=True)
  class Meta:
    model = Project
    fields = ['p_id', 'title', 'images']

class UserSerializer(serializers.ModelSerializer):
  projects = ProjectSerializer(many=True, read_only=True)
  class Meta:
    model = User
    fields = ['u_id', 'name', 'mail', 'password', 'projects']
