from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from backend_api import views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
schema_view = get_schema_view(openapi.Info(
    title="API",
    default_version="v1.0.0"
))

urlpatterns = [
    path('dzi/<path:file_path>', views.read_dzi),
    path('heatmap/<path:file_path>', views.read_heatmap),
    path('user/', views.UserViewSet.as_view({
        'get': 'get_all_users',
        'post': 'sign_up',
    })),
    path('user/login', views.UserViewSet.as_view({
        'post': 'login',
    })),
    path('project/', views.ProjectViewSet.as_view({
        'get': 'get_db_projects',
    })),
    path('project/<str:pk>', views.ProjectViewSet.as_view({
        'get': 'get_all_projects',
    })),
    path('judgement/', views.JudgementViewSet.as_view({
        'get': 'get_db_judgements',
        'post': 'add_judgement',
    })),
    path('judgement/<str:id>', views.JudgementViewSet.as_view({
        'get': 'get_user_judgements',
    })),
    path('feedback/', views.FeedbackViewSet.as_view({
        'post': 'post_feedback',
    })),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='scheme-redoc')
]