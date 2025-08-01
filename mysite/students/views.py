from rest_framework import viewsets, permissions
from .models import Student
from .serializers import StudentSerializer
from users.permissions import IsAdminUser, IsStaffUser, IsStudentUser

class StudentViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'create', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsStaffUser]
        elif self.action in ['update', 'partial_update', 'retrieve']:
            # For retrieve, we will do a custom check in the method
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        This view should return a list of all the students
        for admin/staff users, or only the current user's student profile.
        """
        user = self.request.user
        if user.is_staff or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'staff']):
            return Student.objects.all()
        elif hasattr(user, 'student_profile'):
            return Student.objects.filter(user=user)
        else:
            # Return an empty queryset if the user is not staff/admin and has no student profile
            return Student.objects.none()

    def retrieve(self, request, *args, **kwargs):
        """
        Allow a student to retrieve their own profile.
        Admin and Staff can retrieve any profile.
        """
        instance = self.get_object()
        user = self.request.user
        
        # Check if the user is the owner of the student profile, or is admin/staff
        if instance.user == user or user.is_staff or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'staff']):
            return super().retrieve(request, *args, **kwargs)
        else:
            # If not authorized, explicitly deny permission
            self.permission_denied(request)

    def update(self, request, *args, **kwargs):
        """
        Allow a student to update their own profile.
        Admin and Staff can update any profile.
        """
        instance = self.get_object()
        user = self.request.user

        if instance.user == user or user.is_staff or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'staff']):
            return super().update(request, *args, **kwargs)
        else:
            self.permission_denied(request)

    def destroy(self, request, *args, **kwargs):
        """
        Only Admin and Staff can delete a student profile.
        """
        if not (self.request.user.is_staff or (hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.role in ['admin', 'staff'])):
            self.permission_denied(request)
        return super().destroy(request, *args, **kwargs)
