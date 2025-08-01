from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from students.models import Student
from projects.models import FinalProject
from advisors.models import Advisor
from users.models import UserProfile

class DashboardAPITests(APITestCase):
    """
    Tests for the Dashboard API endpoint.
    """

    def setUp(self):
        # Create users with different roles
        self.staff_user = User.objects.create_user(username='staff', password='password123', is_staff=True)
        UserProfile.objects.create(user=self.staff_user, role='staff')

        self.student_user = User.objects.create_user(username='student', password='password123')
        UserProfile.objects.create(user=self.student_user, role='student')

        # Create some data to be aggregated
        Student.objects.create(user=self.student_user, student_id='s123', email='s@t.com', first_name='S', last_name='1', major='CS', year_enrolled=2020)
        Advisor.objects.create(email='a@t.com', first_name='A', last_name='1', leading_quota=5, committee_quota=5)
        FinalProject.objects.create(title='P1', description='...')

    def test_dashboard_access_for_staff(self):
        """
        Ensure a staff user can access the dashboard and receives correct data structure.
        """
        # Authenticate as the staff user
        refresh = RefreshToken.for_user(self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = '/api/dashboard/'
        response = self.client.get(url, format='json')

        # 1. Check for a successful response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Check that the top-level keys are present in the response
        self.assertIn('total_students', response.data)
        self.assertIn('total_advisors', response.data)
        self.assertIn('total_projects', response.data)
        self.assertIn('projects_by_status', response.data)
        self.assertIn('advisor_quota_usage', response.data)
        
        # 3. Check a specific value
        self.assertEqual(response.data['total_students'], 1)

    def test_dashboard_access_denied_for_student(self):
        """
        Ensure a non-staff user (like a student) cannot access the dashboard.
        """
        # Authenticate as the student user
        refresh = RefreshToken.for_user(self.student_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = '/api/dashboard/'
        response = self.client.get(url, format='json')

        # Check that the request was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
