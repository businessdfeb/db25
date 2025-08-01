from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count

from students.models import Student
from projects.models import FinalProject
from advisors.models import Advisor
from users.permissions import IsAdminUser, IsStaffUser

class DashboardStatsView(APIView):
    """
    A read-only view that returns summary statistics for the dashboard.
    Accessible only by Admin and Staff users.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | IsStaffUser]

    def get(self, request, format=None):
        """
        Return a dictionary of dashboard statistics.
        """
        # --- Student Stats ---
        total_students = Student.objects.count()
        students_by_status = Student.objects.values('status').annotate(count=Count('status'))
        
        # --- Advisor Stats ---
        total_advisors = Advisor.objects.count()

        # --- Project Stats ---
        total_projects = FinalProject.objects.count()
        projects_by_status = FinalProject.objects.values('status').annotate(count=Count('status'))
        
        # --- Prepare Advisor Quota Usage ---
        # This can be a more expensive query, so we'll be efficient
        advisors_with_project_counts = Advisor.objects.annotate(
            leading_count=Count('leading_projects', distinct=True),
            committee_count=Count('committee_projects', distinct=True)
        ).values('first_name', 'last_name', 'leading_quota', 'committee_quota', 'leading_count', 'committee_count')

        # --- Compile the final data ---
        data = {
            'total_students': total_students,
            'students_by_status': {item['status']: item['count'] for item in students_by_status},
            'total_advisors': total_advisors,
            'total_projects': total_projects,
            'projects_by_status': {item['status']: item['count'] for item in projects_by_status},
            'advisor_quota_usage': list(advisors_with_project_counts)
        }
        
        return Response(data)
