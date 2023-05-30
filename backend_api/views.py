from django.http import JsonResponse,  FileResponse, HttpResponse
from django.core.serializers import serialize
from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Project, Image, Judgement
from .serializers import UserSerializer, ProjectSerializer, ImageSerializer, JudgementSerializer
import os
import glob
# Create your views here.


@api_view(['POST'])
def sign_up(request, format=None):
  if request.method == 'POST':
    serializer = UserSerializer(data = request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def user_list(request, format=None):
  users = User.objects.all()
  if request.method == 'GET':
    serializer= UserSerializer(users, many=True)
    return Response(serializer.data)
  elif request.method == 'POST':
    user = User.objects.get(mail=request.data['mail'], password=request.data['password'])
    projects = Project.objects.filter(u_id=user.u_id)
    serializer = ProjectSerializer(projects, many=True)
    return JsonResponse({
      'message': user.u_id,
      'status': status.HTTP_200_OK
    })
  return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def project_list(request, pk, format=None):
  if request.method == 'GET':
    pathPattern = "/home/nas/DZI/" + pk + r"/*.dzi"
    files = []
    for f in glob.glob(pathPattern):
      filename = f.split('/')[-1]
      name = filename.split('.')[0:2]
      files.append({
        "name": name[0] + '.' + name[1],
        "path": f
      })
    return JsonResponse(files, safe=False)

@api_view(['GET'])
def judgement_list(request, pk, format=None):
  if request.method == 'GET':
    projects = Project.objects.filter(u_id=pk)
    images = Image.objects.filter(p_id_id__in=projects)
    judgements = Judgement.objects.filter(i_id_id__in=images).select_related()
    result = []
    for j in judgements:
      record = {}
      record['title'] = j.i_id.p_id.title
      record['name'] = j.i_id.name
      record['firstJudge'] = j.firstJudge
      record['secondJudge'] = j.secondJudge
      record['firstDuration'] = j.firstDuration
      record['secondDuration'] = j.secondDuration
      record['created_time'] = j.created_time.strftime("%Y-%m-%d %H:%M:%S")
      result.append(record)
    return JsonResponse(result, safe=False)
  return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def read_dzi(request, file_path):
  isImage = '_files' in file_path
  if isImage:
    with open(file_path, 'rb') as f:
      return HttpResponse(f.read(), content_type='image/jpeg')
  else:
    with open(file_path, 'rb') as f: 
      return HttpResponse(f.read(), content_type='application/xml')

@api_view(['POST'])
def post_judgement(request, format=None):
  if request.method == 'POST':
    serializer = JudgementSerializer(data=request.data)
    if request.data['i_id'] is None:
      user = User.objects.get(u_id=request.data['u_id'])
      if len(Project.objects.filter(title=request.data['title'])) == 0:
        Project.objects.create(u_id=user, title=request.data['title'])
      project = Project.objects.get(title=request.data['title'])
      image = Image.objects.create(p_id=project, name=request.data['name'], path=request.data['path'])
      request.data['i_id'] = image.i_id
      serializer = JudgementSerializer(data=request.data)
    if serializer.is_valid():
      image = Image.objects.get(i_id=request.data['i_id'])
      serializer.save(i_id=image)
      return JsonResponse({
      'message': user.u_id,
      'status': status.HTTP_201_CREATED
    })
    return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
