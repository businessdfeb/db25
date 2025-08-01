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
        Check advisor and committee member quotas.
        """
        # --- 1. Check Advisor Leading Quota ---
        advisor = data.get('advisor')
        if advisor:
            is_new_assignment = not (self.instance and self.instance.advisor == advisor)
            if is_new_assignment:
                current_projects_count = FinalProject.objects.filter(advisor=advisor).count()
                if current_projects_count >= advisor.leading_quota:
                    raise serializers.ValidationError({
                        'advisor': f'Advisor {advisor} has reached their leading project limit of {advisor.leading_quota}.'
                    })

        # --- 2. Check Committee Member Quotas ---
        committee = data.get('committee_members')
        if committee:
            for member in committee:
                # Only check quota if the member is being newly added to the committee
                is_new_member = not (self.instance and member in self.instance.committee_members.all())
                if is_new_member:
                    committee_count = FinalProject.objects.filter(committee_members=member).count()
                    if committee_count >= member.committee_quota:
                        raise serializers.ValidationError({
                            'committee_members': f'Advisor {member} has reached their committee limit of {member.committee_quota}.'
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
