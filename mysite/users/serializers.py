from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile
from students.models import Student
from advisors.models import Advisor

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles the creation of User, UserProfile, and the role-specific
    profile (Student or Advisor).
    """
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, write_only=True)
    
    # Student specific fields
    student_id = serializers.CharField(max_length=20, required=False)
    major = serializers.CharField(max_length=100, required=False)
    year_enrolled = serializers.IntegerField(required=False)

    # Advisor specific fields
    department = serializers.CharField(max_length=100, required=False)
    position = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'role', 
                  'student_id', 'major', 'year_enrolled', 'department', 'position']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """
        Validate role-specific fields.
        """
        role = data.get('role')
        if role == 'student':
            if not all([data.get('student_id'), data.get('major'), data.get('year_enrolled')]):
                raise serializers.ValidationError("Student ID, major, and year enrolled are required for student registration.")
        elif role == 'lecturer':
            if not all([data.get('department'), data.get('position')]):
                 raise serializers.ValidationError("Department and position are required for lecturer registration.")
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new user and their associated profiles in a single transaction.
        """
        # Create the base user
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        # Create the user profile for role
        UserProfile.objects.create(user=user, role=validated_data['role'])

        # Create the role-specific profile
        if validated_data['role'] == 'student':
            Student.objects.create(
                user=user,
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                email=validated_data['email'],
                student_id=validated_data['student_id'],
                major=validated_data['major'],
                year_enrolled=validated_data['year_enrolled']
            )
        elif validated_data['role'] == 'lecturer':
            Advisor.objects.create(
                user=user,
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                email=validated_data['email'],
                department=validated_data['department'],
                position=validated_data['position']
            )
            
        return user
