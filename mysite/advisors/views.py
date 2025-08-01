from rest_framework import viewsets, permissions
from .models import Advisor, AdvisorRole
from .serializers import AdvisorSerializer, AdvisorRoleSerializer
from users.permissions import IsAdminUser, IsStaffUser, IsLecturerUser

class AdvisorViewSet(viewsets.ModelViewSet):
    """
    This viewset provides CRUD operations for Advisors.
    - Admins/Staff: Full access.
    - Lecturers: Can view their own profile, can view list.
    - Students: Can view list.
    """
    serializer_class = AdvisorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Set custom permissions for different actions.
        """
        if self.action in ['create', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsStaffUser]
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.IsAuthenticated] # All authenticated users can view
        elif self.action in ['update', 'partial_update']:
             self.permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsStaffUser | IsLecturerUser]
        return super().get_permissions()

    def get_queryset(self):
        """
        Advisors can always be seen by anyone who is authenticated.
        """
        return Advisor.objects.all()

    def perform_update(self, serializer):
        """
        Allow an advisor (lecturer) to update their own profile.
        Admin and Staff can update any profile.
        """
        instance = self.get_object()
        user = self.request.user

        if user.is_staff or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
            serializer.save()
        elif hasattr(user, 'userprofile') and user.userprofile.role == 'lecturer' and instance.user == user:
             serializer.save()
        else:
            self.permission_denied(self.request)

class AdvisorRoleViewSet(viewsets.ModelViewSet):
    """
    This viewset provides CRUD for Advisor Roles.
    Should generally only be managed by Admins.
    """
    queryset = AdvisorRole.objects.all()
    serializer_class = AdvisorRoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
