from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinalProjectViewSet

router = DefaultRouter()
router.register(r'projects', FinalProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
