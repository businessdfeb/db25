from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import FinalProject
from .serializers import FinalProjectSerializer
from users.permissions import IsAdminUser, IsStaffUser, IsStudentUser, IsLecturerUser

class FinalProjectViewSet(viewsets.ModelViewSet):
    """
    This viewset handles CRUD operations for Final Projects.
    Permissions are based on user roles (Student, Advisor, Staff, Admin).
    """
    serializer_class = FinalProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        - Admin/Staff see all projects.
        - Students see projects they are assigned to.
        - Lecturers see projects they are advising or are a committee member of.
        """
        user = self.request.user
        if user.is_staff or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'staff']):
            return FinalProject.objects.all()
        
        queryset = FinalProject.objects.none()
        if hasattr(user, 'student_profile'):
            queryset = queryset.union(FinalProject.objects.filter(students=user.student_profile))
        
        if hasattr(user, 'advisor_profile'):
            queryset = queryset.union(FinalProject.objects.filter(advisor=user.advisor_profile))
            queryset = queryset.union(FinalProject.objects.filter(committee_members=user.advisor_profile))

        return queryset.distinct()

    def create(self, request, *args, **kwargs):
        """
        - A student can create a project and assign themselves.
        - Admin/Staff can create any project.
        """
        user = self.request.user
        if not (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'staff', 'student']):
            return Response({'detail': 'You do not have permission to create a project.'}, status=status.HTTP_403_FORBIDDEN)
        
        # When a student creates a project, automatically add them to it
        if hasattr(user, 'userprofile') and user.userprofile.role == 'student':
            request.data['students'] = [user.student_profile.id]

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        - Students can update their own project's details.
        - Advisors can update the status of projects they advise.
        - Admin/Staff can update anything.
        """
        instance = self.get_object()
        user = self.request.user

        is_admin_or_staff = user.is_staff or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'staff'])
        is_assigned_student = hasattr(user, 'student_profile') and user.student_profile in instance.students.all()
        is_assigned_advisor = hasattr(user, 'advisor_profile') and user.advisor_profile == instance.advisor

        # Allow full update for admin/staff
        if is_admin_or_staff:
            return super().update(request, *args, **kwargs)
        
        # Students can't change the advisor or status
        if is_assigned_student:
            if 'advisor' in request.data or 'status' in request.data:
                 return Response({'detail': 'You cannot change the advisor or status.'}, status=status.HTTP_403_FORBIDDEN)
            return super().update(request, *args, **kwargs)

        # Advisors can only change the status
        if is_assigned_advisor:
            # Only allow 'status' field to be updated by advisor
            for field in request.data:
                if field != 'status':
                    return Response({'detail': f'Advisors can only update the status, not {field}.'}, status=status.HTTP_403_FORBIDDEN)
            return super().update(request, *args, **kwargs)

        return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        """
        Only Admin and Staff can delete a project.
        """
        user = self.request.user
        if not (user.is_staff or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'staff'])):
            return Response({'detail': 'You do not have permission to delete this project.'}, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Admins, staff, assigned students, and assigned advisors can view the project.
        """
        # The get_queryset method already filters this, so if the object is found,
        # the user has permission.
        return super().retrieve(request, *args, **kwargs)
