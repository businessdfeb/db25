from rest_framework import generics, permissions
from .serializers import UserRegistrationSerializer
from django.contrib.auth.models import User

class UserRegistrationView(generics.CreateAPIView):
    """
    Public endpoint for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny] # Allow any user (authenticated or not) to access this endpoint.
