from rest_framework import serializers
from .models import FinalProject, Student, Advisor
from students.serializers import StudentSerializer
from advisors.serializers import AdvisorSerializer

class FinalProjectSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField for writing, allowing assignment by ID.
    students = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Student.objects.all()
    )
    advisor = serializers.PrimaryKeyRelatedField(
        queryset=Advisor.objects.all(),
        allow_null=True # Allow projects to be created without an advisor initially
    )
    committee_members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Advisor.objects.all(),
        required=False # Committee members are optional
    )

    class Meta:
        model = FinalProject
        fields = [
            'id', 'title', 'description', 'submission_date', 
            'status', 'students', 'advisor', 'committee_members'
        ]

    def validate(self, data):
        """
        Check that the advisor has not exceeded their leading quota.
        """
        # Get the advisor being assigned, if any
        advisor = data.get('advisor')

        if advisor:
            # Check if this is an update and if the advisor is unchanged
            if self.instance and self.instance.advisor == advisor:
                # Advisor is not being changed, so no need to check quota
                return data

            # Count the number of projects the advisor is currently leading
            current_projects_count = FinalProject.objects.filter(advisor=advisor).count()
            
            # Check against their quota
            if current_projects_count >= advisor.leading_quota:
                raise serializers.ValidationError({
                    'advisor': f'Advisor {advisor} has reached their project limit of {advisor.leading_quota}.'
                })
        
        return data

    def to_representation(self, instance):
        """
        Customize the output representation to show nested objects for reading.
        """
        representation = super().to_representation(instance)
        # For reading, we want to show the full student and advisor objects
        representation['students'] = StudentSerializer(instance.students.all(), many=True).data
        if instance.advisor:
            representation['advisor'] = AdvisorSerializer(instance.advisor).data
        if instance.committee_members:
            representation['committee_members'] = AdvisorSerializer(instance.committee_members.all(), many=True).data
        return representation
