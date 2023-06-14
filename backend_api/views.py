from django.http import JsonResponse,  FileResponse, HttpResponse
from django.core.serializers import serialize
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, Project, Image, Judgement, Feedback
from .serializers import UserSerializer, ProjectSerializer, ImageSerializer, JudgementSerializer, FeedbackSerializer
import os
import glob
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  
  @action(detail=False, methods=['get'])
  @swagger_auto_schema(
    operation_summary='Get all users from the database'
  )
  def get_all_users(self, request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

  @action(detail=False, methods=['post'])
  @swagger_auto_schema(
    operation_summary='Create a new user account',
    responses={
      201: openapi.Response(
        description="Successful created",
        schema=openapi.Schema(
          type=openapi.TYPE_OBJECT,
          properties={
            'u_id': openapi.Schema(
              type=openapi.TYPE_INTEGER,
              description="User ID"
            ),
            'name': openapi.Schema(
              type=openapi.TYPE_STRING,
              description="User name"
            ),
            'mail': openapi.Schema(
              type=openapi.TYPE_STRING, 
              description="User mail"
            )
          }
        )
      ),
      409: openapi.Response(
        description="Account existed",
        schema=openapi.Schema(
          type=openapi.TYPE_OBJECT,
          properties={
            'message': openapi.Schema(
              type=openapi.TYPE_STRING,
              description="The email has been registered!"
            )
          }
        )
      )
    }
  )
  def sign_up(self, request):
    try:
      user = User.objects.get(mail=request.data['mail'])
      return JsonResponse({
        'message': 'The email has been registered!',
        'status': status.HTTP_409_CONFLICT
      })
    except:
      try:
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
          serializer.save()
          user = User.objects.get(mail=request.data['mail'])
          return JsonResponse({
            'message': {
              'u_id': user.u_id,
              'name': user.name,
              'mail': user.mail
            },
            'status': status.HTTP_201_CREATED
          })
      except:
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  @action(detail=True, methods=['post'])  
  @swagger_auto_schema(
    operation_summary='User login',
    request_body=openapi.Schema(
      type=openapi.TYPE_OBJECT,
      properties={
        'mail': openapi.Schema(
          type=openapi.TYPE_STRING,
          in_=openapi.IN_QUERY,
          description="User mail"
        ),
        'password': openapi.Schema(
          type=openapi.TYPE_STRING,
          in_=openapi.IN_QUERY,
          description="User password"
        )
      }
    ),
    responses={
      200: openapi.Response(
        description="Successful login",
        schema=openapi.Schema(
          type=openapi.TYPE_OBJECT,
          properties={
            'u_id': openapi.Schema(
              type=openapi.TYPE_INTEGER,
              description="User ID"
            ),
            'name': openapi.Schema(
              type=openapi.TYPE_STRING,
              description="User name"
            ),
            'mail': openapi.Schema(
              type=openapi.TYPE_STRING, 
              description="User mail"
            )
          }
        )
      ),
      422: openapi.Response(
        description="Invalid credentials",
        schema=openapi.Schema(
          type=openapi.TYPE_OBJECT,
          properties={
            'message': openapi.Schema(
              type=openapi.TYPE_STRING,
              description="Email or password is wrong!"
            )
          }
        )
      )
    }
  )
  def login(self, request):
    try:
      user = User.objects.get(mail=request.data['mail'], password=request.data['password'])
    except User.DoesNotExist:
      return JsonResponse({
        'message': 'Email or password is wrong!',
        'status': status.HTTP_422_UNPROCESSABLE_ENTITY
      })
    projects = Project.objects.filter(u_id=user.u_id)
    serializer = ProjectSerializer(projects, many=True)
    return JsonResponse({
      'message': {
          'u_id': user.u_id,
          'name': user.name,
          'mail': user.mail
        },
      'status': status.HTTP_200_OK
    })
    return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProjectViewSet(viewsets.ModelViewSet):

  queryset=Project.objects.all()
  serializer_class=ProjectSerializer
  @action(detail=False,  methods=['get'])
  @swagger_auto_schema(
    operation_summary='Get all projects from the database',
  )
  def get_db_projects(self, request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

  @action(detail=False, methods=['get'])
  @swagger_auto_schema(
    operation_summary='Get all images of the related organ from the server'
  )
  def get_all_projects(self, request, pk):
    pathPattern = "/home/nas/DZI/" + pk + r"/*.dzi"
    files = []
    for f in glob.glob(pathPattern):
      filename = f.split('/')[-1]
      name = filename.split('.')[0:2]
      files.append({
        "name": name[0] + '.' + name[1],
        "path": f
      })
    if len(files) > 0:
      return JsonResponse(files, safe=False)
    else:
      return JsonResponse({
        'message': 'No related files!', 
        'status': status.HTTP_404_NOT_FOUND
      })

class JudgementViewSet(viewsets.ModelViewSet):  

  @action(detail=False,  methods=['get'])
  @swagger_auto_schema(
    operation_summary='Get all judgements from the database'
  )
  def get_db_judgements(self, request):
    judgements = Judgement.objects.all()
    serializer = JudgementSerializer(judgements, many=True)
    return Response(serializer.data)

  @action(detail=False, methods=['get'])
  @swagger_auto_schema(
    operation_summary='Get all judgements of the user from the database'
  )
  def get_user_judgements(self, request, id):
    try:
      projects = Project.objects.filter(u_id=id)
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
    except:
      return JsonResponse({
        'message': 'No related files!', 
        'status': status.HTTP_404_NOT_FOUND
      })

  queryset = Judgement.objects.all()
  serializer_class = JudgementSerializer
  @action(detail=False, methods=['post'])
  @swagger_auto_schema(
    operation_summary='Create judgement from the user response',
    request_body=openapi.Schema(
      type=openapi.TYPE_OBJECT,
      properties={
        'u_id': openapi.Schema(
          type=openapi.TYPE_INTEGER,
          in_=openapi.IN_BODY,
          description="User ID"
        ),
        'i_id': openapi.Schema(
          type=openapi.TYPE_INTEGER,
          in_=openapi.IN_BODY,
          description="Image IDv"
        ),
        'title': openapi.Schema(
          type=openapi.TYPE_STRING,
          in_=openapi.IN_BODY,
          description="Project Title"
        ),
        'name': openapi.Schema(
          type=openapi.TYPE_STRING,
          in_=openapi.IN_BODY,
          description="Image name"
        ),
        'path': openapi.Schema(
          type=openapi.TYPE_STRING,
          in_=openapi.IN_BODY,
          description="Image path"
        ),
        'firstJudge': openapi.Schema(
          type=openapi.TYPE_STRING,
          in_=openapi.IN_BODY,
          description="First judgement"
        ),        
        'secondJudge': openapi.Schema(
          type=openapi.TYPE_STRING,
          in_=openapi.IN_BODY,
          description="Second judgement"
        ),
        'firstDuration': openapi.Schema(
          type=openapi.TYPE_STRING,
          in_=openapi.IN_BODY,
          description="First duration"
        ),
        'secondDuration': openapi.Schema(
          type=openapi.TYPE_STRING,
          in_=openapi.IN_BODY,
          description="Second duration"
        ),
      }
    ),
    responses={
      201: openapi.Response(
        description="Successful created",
        schema=openapi.Schema(
          type=openapi.TYPE_OBJECT,
          properties={
            'u_id': openapi.Schema(
              type=openapi.TYPE_INTEGER,
              description="User ID"
            ),
          }
        )
      )
    }
  )
  def add_judgement(self, request):
    try:
      serializer = JudgementSerializer(data=request.data)
      user=User.objects.get(u_id=request.data['u_id'])
      project = Project.objects.filter(u_id=user, title=request.data['title'])
      if project.exists():
        pass
      else:
        Project.objects.create(u_id=user, title=request.data['title'])
      if request.data['i_id'] is None:
        project = Project.objects.get(u_id=user, title=request.data['title'])
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
    except:
      return JsonResponse({
        'message': 'Bad request',
        'status': status.HTTP_400_BAD_REQUEST
      })
        

@api_view(['GET'])
def read_dzi(request, file_path):
  isImage = '_files' in file_path
  if isImage:
    with open(file_path, 'rb') as f:
      return HttpResponse(f.read(), content_type='image/jpeg')
  else:
    with open(file_path, 'rb') as f: 
      return HttpResponse(f.read(), content_type='application/xml')

@api_view(['GET'])
@swagger_auto_schema(
  operation_summary='Return heatmap image'
)
def read_heatmap(request, file_path):
  with open(file_path, 'rb') as f:
    return HttpResponse(f.read(), content_type='image/png')

class FeedbackViewSet(viewsets.ModelViewSet):
  queryset = Feedback.objects.all()
  serializer_class = FeedbackSerializer
  @action(detail=False, methods=['post'])
  def post_feedback(self, request):
    try:
      serializer = FeedbackSerializer(data = request.data)
      if serializer.is_valid():
        serializer.save()
        feedback = Feedback.objects.get(email=request.data['email'])
        return JsonResponse({
          'message': {
            'firstName': feedback.firstName,
            'lastName': feedback.lastName,
            'email': feedback.email,
            'message': feedback.message,
          },
          'status': status.HTTP_201_CREATED
        })
    except:
      return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)