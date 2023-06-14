from rest_framework import serializers
from .models import User, Project, Image, Judgement, Feedback

class JudgementSerializer(serializers.ModelSerializer):
  class Meta:
    model = Judgement
    fields = ['firstJudge', 'secondJudge', 'firstDuration', 'secondDuration', 'created_time']

class ImageSerializer(serializers.ModelSerializer):
  judgements = JudgementSerializer(many=True)
  class Meta:
    model = Image
    fields = ['name', 'judgements']

class ProjectSerializer(serializers.ModelSerializer):
  images = ImageSerializer(many=True)
  class Meta:
    model = Project
    fields = ['title', 'images']

class UserSerializer(serializers.ModelSerializer):
  projects = ProjectSerializer(many=True, read_only=True)
  class Meta:
    model = User
    fields = ['u_id', 'name', 'mail', 'password', 'projects']

class FeedbackSerializer(serializers.ModelSerializer):
  class Meta:
    model = Feedback
    fields = ['f_id', 'firstName', 'lastName', 'email', 'message']