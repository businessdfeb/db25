from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from advisors.models import Advisor
from students.models import Student
from .models import FinalProject
from users.models import UserProfile

class ProjectAPITests(APITestCase):
    """
    Tests for the FinalProject API, including quota validation and permissions.
    """

    def setUp(self):
        # --- Create Users and Profiles ---
        self.staff_user = User.objects.create_user(username='staff', password='password123', is_staff=True)
        UserProfile.objects.create(user=self.staff_user, role='staff')

        self.student_user = User.objects.create_user(username='student', password='password123')
        self.student_profile = Student.objects.create(user=self.student_user, student_id='s123', email='student@test.com', first_name='Test', last_name='Student', major='CS', year_enrolled=2020)
        UserProfile.objects.create(user=self.student_user, role='student')
        
        self.advisor_user = User.objects.create_user(username='advisor', password='password123')
        self.advisor = Advisor.objects.create(
            user=self.advisor_user, 
            email='advisor@test.com', 
            first_name='Dr.', last_name='Advisor', 
            leading_quota=1,
            committee_quota=1 # Set a small quota for easy testing
        )
        UserProfile.objects.create(user=self.advisor_user, role='lecturer')

        # --- Create a pre-existing project to fill the advisor's quotas ---
        self.existing_project = FinalProject.objects.create(
            title="Existing Project", 
            advisor=self.advisor,
            description="A project that already exists."
        )
        self.existing_project.students.add(self.student_profile)
        self.existing_project.committee_members.add(self.advisor) # Also add as committee member

    def test_advisor_leading_quota_limit(self):
        """
        Ensure a project cannot be created if the advisor's leading_quota is full.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.staff_user).access_token}')
        new_project_data = {
            'title': 'New Project That Should Fail', 'description': '...', 'advisor': self.advisor.id, 'students': [self.student_profile.id]
        }
        response = self.client.post('/api/projects/', new_project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('has reached their leading project limit', str(response.data['advisor'][0]))
        self.assertEqual(FinalProject.objects.count(), 1)

    def test_committee_member_quota_limit(self):
        """
        Ensure a project cannot be created if a committee member's quota is full.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.staff_user).access_token}')
        # This advisor's committee quota is already full from the setUp method
        new_project_data = {
            'title': 'Another Project That Should Fail', 'description': '...', 'committee_members': [self.advisor.id], 'students': [self.student_profile.id]
        }
        response = self.client.post('/api/projects/', new_project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('committee_members', response.data)
        self.assertIn('has reached their committee limit', str(response.data['committee_members'][0]))
        self.assertEqual(FinalProject.objects.count(), 1)

    def test_student_cannot_delete_project(self):
        """
        Ensure a user with the 'student' role cannot delete a project.
        """
        # Authenticate as the student
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.student_user).access_token}')
        
        url = f'/api/projects/{self.existing_project.id}/'
        response = self.client.delete(url)
        
        # --- Assertions ---
        # 1. Check that the request was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 2. Verify that the project was NOT deleted
        self.assertEqual(FinalProject.objects.count(), 1)

    def test_project_creation_succeeds_with_available_quota(self):
        """
        Ensure a project CAN be created if the advisor has available quota.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.staff_user).access_token}')
        new_advisor_user = User.objects.create_user(username='newadvisor', password='password123')
        available_advisor = Advisor.objects.create(user=new_advisor_user, email='newadvisor@test.com', first_name='Dr.', last_name='Available', leading_quota=2)
        UserProfile.objects.create(user=new_advisor_user, role='lecturer')
        
        project_data = {'title': 'Project That Should Succeed', 'description': '...', 'advisor': available_advisor.id, 'students': [self.student_profile.id]}
        response = self.client.post('/api/projects/', project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FinalProject.objects.count(), 2)
