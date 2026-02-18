from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserViewSet, RoleViewSet, LogViewSet, SoapViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'logs', LogViewSet)
router.register(r'soap', SoapViewSet, basename='soap')

urlpatterns = [
    path('auth/login/', obtain_auth_token, name='api_token_auth'),
    path('', include(router.urls)),
]
