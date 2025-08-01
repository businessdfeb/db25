from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdvisorViewSet, AdvisorRoleViewSet

router = DefaultRouter()
router.register(r'advisors', AdvisorViewSet, basename='advisor')
router.register(r'advisorroles', AdvisorRoleViewSet, basename='advisorrole')

urlpatterns = [
    path('', include(router.urls)),
]
